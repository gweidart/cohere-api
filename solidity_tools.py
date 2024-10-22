# solidity_tools.py
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
import re

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
# Contract Template for SPDX and Pragma Solidity
# -------------------------------

CONTRACT_TEMPLATE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

"""

# Helper function to prepend the template to generated contracts
def generate_contract_with_template(contract_body: str) -> str:
    """
    Prepend the contract body with the SPDX identifier and solidity version pragma.
    """
    return CONTRACT_TEMPLATE + contract_body

# -------------------------------
# Helper Function for Sequential Naming
# -------------------------------

def get_next_filename(directory: str, extension: str) -> int:
    """
    Get the next available sequential filename number in the given directory.
    Files are named as 0.extension, 1.extension, 2.extension, etc.
    """
    # Ensure the directory exists, if not create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # List all files in the directory
    files = os.listdir(directory)

    # Extract numbers from filenames using regex
    numbers = []
    for file in files:
        match = re.match(r"(\d+)\." + extension, file)
        if match:
            numbers.append(int(match.group(1)))

    # Return the next available number
    return max(numbers) + 1 if numbers else 0

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
        result = subprocess.run(['solc', temp_file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            logger.error(f"Compilation failed: {result.stderr.decode()}")
            return f"Compilation failed: {result.stderr.decode()}"  # Return the error message

        return result.stdout.decode()  # Return the compiled contract binary

    except Exception as e:
        logger.error(f"Error during compilation: {e}")
        return f"Error during compilation: {e}"  # Return the error message


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
            return f"Slither analysis failed: {result.stderr.decode()}"  # Return the error message

        return result.stdout.decode()  # Return the analysis report

    except Exception as e:
        logger.error(f"Error during Slither analysis: {e}")
        return f"Error during Slither analysis: {e}"  # Return the error message


@tool(
    args_schema=SaveContractAndReportInput,
    return_direct=True
)
def save_contract_and_report(
    contract_code: str, 
    slither_output: str, 
    contract_filename: Optional[str] = None, 
    report_filename: Optional[str] = None, 
    save_directory: Optional[str] = "saved_contracts"
) -> str:
    """Saves the Solidity contract and Slither report with dynamic naming to prevent overwriting."""
    try:
        # Ensure the contract and report directories exist
        os.makedirs(os.path.join(save_directory, GENERATED_CONTRACT_DIR), exist_ok=True)
        os.makedirs(os.path.join(save_directory, GENERATED_REPORT_DIR), exist_ok=True)

        # Get the next available file number in the contract directory
        next_number = get_next_filename(os.path.join(save_directory, GENERATED_CONTRACT_DIR), 'sol')

        # Define filenames dynamically if not provided
        contract_filename = contract_filename or f"{next_number}.sol"
        report_filename = report_filename or f"{next_number}_slither.json"

        # Apply the contract template (SPDX identifier and pragma solidity)
        contract_code_with_template = generate_contract_with_template(contract_code)

        # Define full paths
        contract_path = os.path.join(save_directory, GENERATED_CONTRACT_DIR, contract_filename)
        report_path = os.path.join(save_directory, GENERATED_REPORT_DIR, report_filename)

        # Save the Solidity contract
        with open(contract_path, 'w') as f:
            f.write(contract_code_with_template)
        pprint(f"Saved Solidity contract to {contract_path}")

        # Save the Slither report
        with open(report_path, 'w') as f:
            f.write(slither_output)
        pprint(f"Saved Slither report to {report_path}")

        # Return success message with file paths
        return f"Files saved successfully:\n- Contract: {contract_path}\n- Slither Report: {report_path}"

    except Exception as e:
        logger.error(f"Error saving files: {e}", exc_info=True)
        return f"Error: {e}"  # Return the error message
