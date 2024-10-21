# tools.py

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

class AssessComplexityAndVulnerabilitiesInput(BaseModel):
    # No inputs required for this tool
    pass

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as tmp_file:
            tmp_file.write(contract_code)
            temp_filename = tmp_file.name
        logger.info(f"Temporary contract file created at {temp_filename}")

        try:
            logger.info("Compiling Solidity contract...")
            result = subprocess.run(['solc', '--bin', temp_filename], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Compilation failed: {result.stderr}")
                return f"Compilation failed: {result.stderr}"
            logger.info("Compilation successful.")
            return "Compilation successful."
        finally:
            os.remove(temp_filename)
            logger.info(f"Temporary contract file {temp_filename} deleted.")

    except Exception as e:
        logger.error(f"Error during compilation: {e}")
        return f"Compilation error: {e}"

@tool(
    args_schema=AnalyzeWithSlitherInput,
    return_direct=True
)
def analyze_with_slither(contract_code: str) -> str:
    """Analyzes the Solidity contract with Slither."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as tmp_file:
            tmp_file.write(contract_code)
            temp_filename = tmp_file.name
        logger.info(f"Temporary contract file created at {temp_filename}")

        try:
            logger.info("Analyzing Solidity contract with Slither...")
            result = subprocess.run(['slither', temp_filename], capture_output=True, text=True)
            if result.returncode != 0 and "No issues detected" not in result.stdout:
                logger.warning(f"Slither analysis found issues: {result.stdout}")
                return f"Slither analysis found issues:\n{result.stdout}"
            logger.info("Slither analysis completed.")
            return result.stdout if result.stdout else "Slither analysis completed with no issues detected."
        finally:
            os.remove(temp_filename)
            logger.info(f"Temporary contract file {temp_filename} deleted.")

    except Exception as e:
        logger.error(f"Error during Slither analysis: {e}")
        return f"Slither analysis error: {e}"

@tool(
    args_schema=SaveContractAndReportInput,
    return_direct=True
)
def save_contract_and_report(
    contract_code: str,
    slither_output: str,
    contract_filename: Optional[str] = None,
    report_filename: Optional[str] = None,
    save_directory: str = "saved_contracts"
) -> str:
    """Saves the Solidity contract and Slither report to files."""
    try:
        # Ensure the save directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            logger.info(f"Created directory: {save_directory}")

        # Generate filenames with timestamp if not provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not contract_filename:
            contract_filename = f"contract_{timestamp}.sol"
        if not report_filename:
            report_filename = f"slither_report_{timestamp}.txt"

        # Define full paths
        contract_path = os.path.join(save_directory, contract_filename)
        report_path = os.path.join(save_directory, report_filename)

        # Save the Solidity contract
        with open(contract_path, 'w') as f:
            f.write(contract_code)
        logger.info(f"Saved Solidity contract to {contract_path}")

        # Save the Slither report
        with open(report_path, 'w') as f:
            f.write(slither_output)
        logger.info(f"Saved Slither report to {report_path}")

        return f"Files saved successfully:\n- Contract: {contract_path}\n- Slither Report: {report_path}"

    except Exception as e:
        logger.error(f"Error saving files: {e}")
        return f"Error saving files: {e}"

@tool(
    args_schema=AssessComplexityAndVulnerabilitiesInput,
    return_direct=True
)
def assess_complexity_and_vulnerabilities() -> str:
    """Returns the contract complexity level and selects which vulnerabilities you need to include in the solidity source code you generate."""
    try:
        # Define complexity levels
        complexity_levels = ["low", "medium", "high"]
        complexity = random.choice(complexity_levels)

        # Randomly select vulnerabilities without repetition
        selected_vulnerabilities = random.sample(VULNERABILITIES, k=random.randint(1, 5))

        # Format the result
        result = f"Complexity Level: {complexity.capitalize()}\n"
        if selected_vulnerabilities:
            result += "Identified Vulnerabilities:\n"
            for vuln in selected_vulnerabilities:
                result += f"- {vuln}\n"
        else:
            result += "No vulnerabilities identified."

        logger.info(f"Assessed complexity as '{complexity}' with vulnerabilities: {selected_vulnerabilities if selected_vulnerabilities else 'None'}")
        return result.strip()

    except Exception as e:
        logger.error(f"Error assessing complexity and vulnerabilities: {e}")
        return f"Error assessing complexity and vulnerabilities: {e}"
