# storage.py

import os

class ContractStorage:
    def __init__(self, base_dir="contracts"):
        self.base_dir = os.path.join(os.getcwd(), base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def save_contract(self, contract_text, complexity, vulnerability_status, contract_name):
        """Saves contract and slither report based on its classification."""
        dir_path = os.path.join(self.base_dir, complexity, vulnerability_status)
        os.makedirs(dir_path, exist_ok=True)
        
        # Save the contract
        contract_file = os.path.join(dir_path, f"{contract_name}.sol")
        with open(contract_file, 'w') as f:
            f.write(contract_text)
        
        return contract_file
