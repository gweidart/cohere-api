# config.py

import os

# Directory Paths
OUTPUT_DIR = 'save_directory'
GENERATED_CONTRACT_DIR = os.path.join(OUTPUT_DIR, 'contracts')
GENERATED_REPORT_DIR = os.path.join(OUTPUT_DIR, 'reports')

# Validation Tools
SOLC_PATH = 'solc'  # Ensure solc is installed and in PATH
SLITHER_PATH = 'slither'  # Ensure Slither is installed and in PATH
