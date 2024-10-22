# tools.py
from config import GENERATED_CONTRACT_DIR, GENERATED_REPORT_DIR
from typing import Type, Optional, Tuple, List
from langchain.tools import tool
from pydantic import BaseModel, Field
import subprocess
import os
import logging
from datetime import datetime
import random
import tempfile
from utils import VULNERABILITIES, COMPLEXITY
from rich.pretty import pprint

# Configure logging
logger = logging.getLogger(__name__)

# -------------------------------
# Input Schema Definitions
# -------------------------------

class CompileSolidityInput(BaseModel):
    contract_code: str = Field(..., description="Solidity contract code to compile.")

class AnalyzeWithSlitherInput(BaseModel):
    contract_code: str = Field(..., description="Solidity contract code to analyze.")

class SaveContractAndReportInput(BaseModel):
    contract_code: str = Field(..., description="Solidity contract code to save.")
    slither_output: str = Field(..., description="Slither analysis report to save.")
    contract_filename: Optional[str] = Field(
        default=None, 
        description="Desired filename for the Solidity contract (e.g., MyContract.sol). If not provided, a timestamped filename will be used."
    )
    report_filename: Optional[str] = Field(
        default=None, 
        description="Desired filename for the Slither report (e.g., MyContract_SlitherReport.txt). If not provided, a timestamped filename will be used."
    )
    save_directory: Optional[str] = Field(
        default="saved_contracts", 
        description="Directory where the files will be saved. Defaults to 'saved_contracts' in the current working directory."
    )

# -------------------------------
# Tool Definitions Using @tool
# -------------------------------

@tool(
    args_schema=CompileSolidityInput,
    return_direct=True
)
def compile_solidity(contract_code: str) -> str:
    """Compiles the Solidity contract."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.sol', delete=False) as temp_file:
            temp_file.write(contract_code.encode())
            temp_file.flush()
            pprint(f"Temporary Solidity file created at {temp_file.name}")

        # Compile the contract using solc
        result = subprocess.run(['solc', '--optimize', '--bin', temp_file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"Compilation failed: {result.stderr.decode()}")

        return result.stdout.decode()

    except Exception as e:
        logger.error(f"Error during compilation: {e}")

@tool(
    args_schema=AnalyzeWithSlitherInput,
    return_direct=True
)
def analyze_with_slither(contract_code: str) -> str:
    """Analyzes the Solidity contract using Slither."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.sol', delete=False) as temp_file:
            temp_file.write(contract_code.encode())
            temp_file.flush()
            pprint(f"Temporary Solidity file created for Slither analysis at {temp_file.name}")

        # Analyze the contract using Slither
        result = subprocess.run(['slither', temp_file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"Slither analysis failed: {result.stderr.decode()}")

        return result.stdout.decode()

    except Exception as e:
        logger.error(f"Error during Slither analysis: {e}")

@tool(
    args_schema=SaveContractAndReportInput,
    return_direct=True
)
def save_contract_and_report(contract_code: str, slither_output: str, contract_filename: Optional[str], report_filename: Optional[str], save_directory: Optional[str]) -> str:
    """Saves the Solidity contract and Slither report."""
    try:
        # Define filenames if not provided
        if not contract_filename:
            contract_filename = f"contract_{datetime.now().strftime('%H%M%S')}.sol"
        if not report_filename:
            report_filename = contract_filename.replace(".sol", "_SlitherReport.txt")

        # Ensure the save directory exists
        os.makedirs(save_directory, exist_ok=True)
        pprint(f'Created directory or already exists: {save_directory}')

        # Define full paths
        contract_path = os.path.join(save_directory, GENERATED_CONTRACT_DIR, contract_filename)
        report_path = os.path.join(save_directory, GENERATED_REPORT_DIR, report_filename)

        # Save the Solidity contract
        with open(contract_path, 'w') as f:
            f.write(contract_code)
        pprint(f"Saved Solidity contract to {contract_path}")

        # Save the Slither report
        with open(report_path, 'w') as f:
            f.write(slither_output)
        pprint(f"Saved Slither report to {report_path}")

        pprint(f"Files saved successfully:\n- Contract: {contract_path}\n- Slither Report: {report_path}")

    except Exception as e:
        logger.error(f"Error saving files: {e}")

