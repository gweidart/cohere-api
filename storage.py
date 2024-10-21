# storage.py

import os
from datetime import datetime
import logging
import json

from config import GENERATED_CONTRACTS_DIR, VALIDATED_CONTRACTS_DIR, LABELED_CONTRACTS_DIR

class ContractStorage:
    def __init__(self):
        self._create_directories()

    def _create_directories(self):
        try:
            os.makedirs(GENERATED_CONTRACTS_DIR, exist_ok=True)
            os.makedirs(VALIDATED_CONTRACTS_DIR, exist_ok=True)
            os.makedirs(LABELED_CONTRACTS_DIR, exist_ok=True)
            logger.info("Output directories created or already exist.")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise e

    def save_generated_contract(self, contract_code: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"contract_{timestamp}.sol"
        filepath = os.path.join(GENERATED_CONTRACTS_DIR, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(contract_code)
            logger.info(f"Generated contract saved at {filepath}.")
            return filepath
        except Exception as e:
            logger.error(f"Error saving generated contract: {e}")
            raise e

    def save_validated_contract(self, contract_code: str, validation_results: dict) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"validated_contract_{timestamp}.sol"
        filepath = os.path.join(VALIDATED_CONTRACTS_DIR, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(contract_code)
            # Save validation results as JSON
            json_filepath = filepath.replace('.sol', '_validation.json')
            with open(json_filepath, 'w') as f:
                json.dump(validation_results, f, indent=4)
            logger.info(f"Validated contract and results saved at {filepath} and {json_filepath}.")
            return filepath
        except Exception as e:
            logger.error(f"Error saving validated contract: {e}")
            raise e

    def save_labeled_contract(self, contract_code: str, labels: dict) -> str:
        if labels.get('status') == 'valid':
            vulnerability = labels.get('vulnerabilities', ['no_vulnerabilities'])[0]
            complexity = labels.get('complexity', 'unknown')
        else:
            vulnerability = 'invalid'
            complexity = 'unknown'

        dir_path = os.path.join(LABELED_CONTRACTS_DIR, vulnerability.replace(' ', '_'), complexity)
        os.makedirs(dir_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"labeled_contract_{timestamp}.sol"
        filepath = os.path.join(dir_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(contract_code)
            # Save labels as JSON
            json_filepath = filepath.replace('.sol', '_labels.json')
            with open(json_filepath, 'w') as f:
                json.dump(labels, f, indent=4)
            logger.info(f"Labeled contract and labels saved at {filepath} and {json_filepath}.")
            return filepath
        except Exception as e:
            logger.error(f"Error saving labeled contract: {e}")
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
            report_filepath = os.path.join(VALIDATED_CONTRACTS_DIR, report_filename)
            with open(report_filepath, 'w') as f:
                f.write(slither_report)
            logger.info(f"Slither report saved at {report_filepath}.")
            return report_filepath
        except Exception as e:
            logger.error(f"Error saving Slither report: {e}")
            raise e
