# tools.py

from langchain_core.tools import tool  # Adjust import based on actual LangChain version
import subprocess
import os
from pydantic import BaseModel, Field
from rich.pretty import pprint
import logging as logger

@tool
def compile_solidity(contract_code: str) -> str:
    """
    Compiles the given Solidity contract using solc to check for syntax and compilation errors.
    """
    try:
        with open('temp_contract.sol', 'w') as f:
            f.write(contract_code)
        result = subprocess.run(['solc', '--bin', 'temp_contract.sol'], capture_output=True, text=True)
        os.remove('temp_contract.sol')
        if result.returncode != 0:
            logger.warning(f"Compilation failed: {result.stderr}")
            return f"Compilation failed: {result.stderr}"
        logger.debug("Compilation successful.")
        return "Compilation successful."
    except Exception as e:
        logger.error(f"Error during compilation: {e}")
        return f"Compilation error: {e}"

class CompileSolidityInput(BaseModel):
    contract_code: str = Field(description="Solidity contract code to compile.")

compile_solidity.name = "compile_solidity"
compile_solidity.description = "Compiles a Solidity smart contract to check for syntax and compilation errors."
compile_solidity.args_schema = CompileSolidityInput

@tool
def analyze_with_slither(contract_code: str) -> str:
    """
    Analyzes the given Solidity contract using Slither to detect vulnerabilities.
    """
    try:
        with open('temp_contract.sol', 'w') as f:
            f.write(contract_code)
        result = subprocess.run(['slither', 'temp_contract.sol'], capture_output=True, text=True)
        os.remove('temp_contract.sol')
        if result.returncode != 0 and "No issues detected" not in result.stdout:
            logger.warning(f"Slither analysis found issues: {result.stdout}")
            return f"Slither analysis found issues: {result.stdout}"
        logger.debug("Slither analysis completed.")
        return result.stdout
    except Exception as e:
        logger.error(f"Error during Slither analysis: {e}")
        return f"Slither analysis error: {e}"

class AnalyzeWithSlitherInput(BaseModel):
    contract_code: str = Field(description="Solidity contract code to analyze.")

analyze_with_slither.name = "analyze_with_slither"
analyze_with_slither.description = "Analyzes a Solidity smart contract for vulnerabilities using Slither."
analyze_with_slither.args_schema = AnalyzeWithSlitherInput

def validate_with_retry(self, contract_name, max_retries=3):
    """Attempts to compile the contract with retries if it fails."""
    retries = 0
    while retries < max_retries:
        logging.info(f"Attempting to compile {contract_name} (Attempt {retries + 1}/{max_retries})")
        compile_result = self.compile_contract()
        if compile_result.returncode == 0:
            logging.info(f"Compilation succeeded for {contract_name}")
            return self.analyze_security(contract_name)
        else:
            retries += 1
            logging.error(f"Compilation failed for {contract_name}, retrying ({retries}/{max_retries})")
        
    logging.error(f"Compilation failed for {contract_name} after {max_retries} retries.")
    return None




