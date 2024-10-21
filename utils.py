import os
import random

# List of vulnerabilities
VULNERABILITIES = [
    'abiencoderv2-array', 'arbitrary-send-erc20', 'arbitrary-send-erc20-permit', 'arbitrary-send-eth',
    'array-by-reference', 'controlled-array-length', 'assert-state-change', 'backdoor', 'weak-prng',
    'boolean-cst', 'boolean-equal', 'shadowing-built-in', 'cache-array-length', 'codex', 'constant-function-asm',
    'constant-function-state', 'controlled-delegatecall', 'costly-loop', 'constable-states', 
    'immutable-states', 'cyclomatic-complexity', 'dead-code', 'delegatecall-loop', 'deprecated-standards',
    'divide-before-multiply', 'domain-separator-collision', 'encode-packed-collision', 'enum-conversion', 
    'external-function', 'function-init-state', 'erc20-interface', 'erc721-interface', 'incorrect-exp', 
    'incorrect-return', 'incorrect-equality', 'incorrect-unary', 'incorrect-using-for', 
    'shadowing-local', 'locked-ether', 'low-level-calls', 'mapping-deletion', 'events-access', 'events-maths', 
    'missing-inheritance', 'missing-zero-check', 'incorrect-modifier', 'msg-value-loop', 'calls-loop', 
    'multiple-constructors', 'name-reused', 'naming-convention', 'out-of-order-retryable', 'variable-scope', 
    'protected-vars', 'public-mappings-nested', 'redundant-statements', 'reentrancy-benign', 'reentrancy-eth', 
    'reentrancy-events', 'reentrancy-unlimited-gas', 'reentrancy-no-eth', 'return-bomb', 'return-leave', 
    'reused-constructor', 'rtlo', 'shadowing-abstract', 'incorrect-shift', 'shadowing-state', 'storage-array', 
    'suicidal', 'tautological-compare', 'timestamp', 'too-many-digits', 'tx-origin', 'tautology', 'unchecked-lowlevel', 
    'unchecked-send', 'unchecked-transfer', 'unimplemented-functions', 'erc20-indexed', 'uninitialized-fptr-cst', 
    'uninitialized-local', 'uninitialized-state', 'uninitialized-storage', 'unprotected-upgrade', 'unused-return', 
    'unused-state', 'var-read-using-this', 'void-cst', 'write-after-write'
]

COMPLEXITY = ['low', 'medium', 'high']

def load_prompt_from_file(filename="prompt.txt"):
    """Loads the contract generation prompt from a .txt file in the CWD."""
    cwd = os.getcwd()
    prompt_path = os.path.join(cwd, filename)
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"The prompt file {filename} was not found in the current working directory.")
    
    with open(prompt_path, 'r') as file:
        return file.read()
        
def load_preamble_from_file(filename="preamble.txt"):
    """Loads the contract generation prompt from a .txt file in the CWD."""
    cwd = os.getcwd()
    preamble_path = os.path.join(cwd, filename)
    
    if not os.path.exists(preamble_path):
        raise FileNotFoundError(f"The preamble file {filename} was not found in the current working directory.")
    
    with open(preamble_path, 'r') as file:
        return file.read()
        
def select_random_vulnerabilities(max_vuln_count=5):
    """Selects a random number and type of vulnerabilities."""
    # Randomly select 1 to max_vuln_count vulnerabilities
    num_vulns = random.randint(1, max_vuln_count)
    return random.sample(VULNERABILITIES, num_vulns)

def select_random_complexity():
    """Selects a random contract complexity level."""
    return random.choice(['low', 'medium', 'high'])
