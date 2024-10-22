# storage.py

import os
from datetime import datetime
import logging
import json
from rich.pretty import pprint
from config import GENERATED_CONTRACT_DIR, GENERATED_REPORT_DIR

class ContractStorage:
    def __init__(self):
        self._create_directories()

    def _create_directories(self):
        try:
            os.makedirs(GENERATED_CONTRACT_DIR, exist_ok=True)
            os.makedirs(GENERATED_REPORT_DIR, exist_ok=True)
            pprint("Output directories created or already exist.")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise e

    def save_generated_contract(self, contract_code: str) -> str:
        timestamp = datetime.now().strftime("%H%M%S%f")
        filename = f"contract_{timestamp}.sol"
        filepath = os.path.join(GENERATED_CONTRACT_DIR, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(contract_code)
            pprint(f"Generated contract saved at {filepath}.")
            return filepath
        except Exception as e:
            logger.error(f"Error saving generated contract: {e}")
            raise e

    def save_slither_report(self, contract_filepath: str, slither_report: str) -> str:
        """
        Saves the Slither analysis report with the same base name as the contract.
        
        Parameters:
            contract_filepath (str): The file path of the validated contract.
            slither_report (str): The Slither analysis report content.
        
        Returns:
            str: The file path where the Slither report is saved.
        """
        try:
            base_name = os.path.splitext(os.path.basename(contract_filepath))[0]
            report_filename = f"{base_name}_slither_report.txt"
            report_filepath = os.path.join(GENERATED_REPORT_DIR, report_filename)
            with open(report_filepath, 'w') as f:
                f.write(slither_report)
            pprint(f"Slither report saved at {report_filepath}.")
            return report_filepath
        except Exception as e:
            logger.error(f"Error saving Slither report: {e}")
            raise e
