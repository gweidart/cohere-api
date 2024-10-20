# solidity_tools.py

import subprocess
import os
import logging
from rich.progress import Progress

class SolidityValidator:
    def __init__(self, contract_text, output_dir="contracts"):
        self.contract_text = contract_text
        self.contract_file = "temp_contract.sol"
        self.output_dir = output_dir

    def compile_contract(self):
        """Compile the Solidity contract using solc."""
        with open(self.contract_file, 'w') as f:
            f.write(self.contract_text)
        
        # Add a progress bar for compilation
        with Progress() as progress:
            task = progress.add_task("[yellow]Compiling contract...", total=100)
            result = subprocess.run(["solc", "--bin", self.contract_file], capture_output=True, text=True)
            progress.update(task, advance=100)
        
        return result

    def analyze_security(self, contract_name):
        """Run Slither on the contract and save the report."""
        report_file = os.path.join(self.output_dir, f"{contract_name}_slither_report.txt")
        
        # Add progress bar for Slither analysis
        with Progress() as progress:
            task = progress.add_task("[red]Analyzing contract with Slither...", total=100)
            result = subprocess.run(["slither --json -", self.contract_file], capture_output=True, text=True)
            progress.update(task, advance=100)
        
        # Save the analysis report
        with open(report_file, 'w') as report:
            report.write(result.stdout)
        
        return report_file

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
