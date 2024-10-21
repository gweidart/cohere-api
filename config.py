# config.py

import os

# Directory Paths
OUTPUT_DIR = 'output_contracts'
GENERATED_CONTRACTS_DIR = os.path.join(OUTPUT_DIR, 'generated')
VALIDATED_CONTRACTS_DIR = os.path.join(OUTPUT_DIR, 'validated')
LABELED_CONTRACTS_DIR = os.path.join(OUTPUT_DIR, 'labeled')

# Validation Tools
SOLC_PATH = 'solc'  # Ensure solc is installed and in PATH
SLITHER_PATH = 'slither'  # Ensure Slither is installed and in PATH
