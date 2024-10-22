import os
import re
import random
import argparse
from rich.logging import RichHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_cohere import ChatCohere, create_cohere_react_agent
from langchain.agents import AgentExecutor
from cohere_api import CohereAPI
from solidity_tools import *
from storage import ContractStorage
from rich.pretty import pprint
from utils import load_preamble_from_file, get_params
from config import GENERATED_CONTRACT_DIR, GENERATED_REPORT_DIR

# Configure Rich logging
logging.basicConfig(
    level="ERROR", format="%(message)s"
)

def parse_assessment_result(assessment_result: str):
    """Parses the string output from the assessment tool and extracts the complexity and vulnerabilities."""
    try:
        # Use regex to extract the complexity level
        complexity_match = re.search(r"Complexity Level: (\w+)", assessment_result)
        complexity = complexity_match.group(1) if complexity_match else None
        
        # Use regex to extract vulnerabilities as a list
        vulnerabilities_match = re.findall(r"- (\w+-\w+)", assessment_result)
        vulnerabilities = vulnerabilities_match if vulnerabilities_match else None
        
        return complexity, vulnerabilities
    except Exception as e:
        logging.error(f"Error parsing assessment result: {e}")
        return None, None

def setup_react_agent(num_contracts):
    # Get the API key from the environment variable
    api_key = os.getenv("COHERE_API_KEY")
    
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY is not set in the environment. Please set it before running the script.")
    
    # Initialize Cohere LLM with the API key for ReAct agent
    cohere_llm = ChatCohere(cohere_api_key=api_key, model="command-r-plus-08-2024")
    chat_hx = [SystemMessage(content="")]
    load_preamble = load_preamble_from_file()
    preamble = load_preamble
    
    # Initialize the CohereAPI to generate contracts
    cohere_api = CohereAPI(api_key)

    # Define the tools for the agent
    tools = [compile_solidity, analyze_with_slither, save_contract_and_report]
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages(chat_hx)
    react_agent = create_cohere_react_agent(llm=cohere_llm, tools=tools, prompt=prompt)
    
    # Execute the agent for each contract to generate
    for i in range(num_contracts):
        pprint(f"Executing agent for contract {i + 1}/{num_contracts}")
        agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)
        
        try:
            logging.info("Starting agent execution with preamble")
            
            # Step 1: Assess complexity and vulnerabilities using the appropriate tool
            logging.info("Assessing complexity and vulnerabilities")
            assessment_result = get_params()

            # Step 2: Parse the assessment result to extract complexity and vulnerabilities
            complexity, vulnerabilities = parse_assessment_result(assessment_result)

            pprint(f"Extracted complexity: {complexity}")
            pprint(f"Extracted vulnerabilities: {vulnerabilities}")

            # Ensure vulnerabilities is a list
            if complexity is None or vulnerabilities is None:
                logging.error(f"Failed to retrieve complexity or vulnerabilities (Complexity: {complexity}, Vulnerabilities: {vulnerabilities})")
                continue
            if not isinstance(vulnerabilities, list):
                logging.error(f"Expected vulnerabilities to be a list, but got {type(vulnerabilities)}")
                continue

            # Step 3: Call CohereAPI to generate the contract code
            logging.info(f"Generating contract with CohereAPI (Complexity: {complexity}, Vulnerabilities: {vulnerabilities})")
            contract_code = cohere_api.generate_contract(complexity, vulnerabilities)
            
            if contract_code is None:
                logging.error("Failed to generate contract, skipping this execution.")
                continue  # Skip to the next contract if generation fails
            
            pprint(f"Generated contract code: {contract_code[:100]}...")  # Log part of the contract code

            # Step 4: Add the tools to the agent's plan for compilation, analysis, and saving
            logging.info("Planning to invoke compile_solidity, analyze_with_slither, and save_contract_and_report...")

            # Compile the contract
            pprint("Invoking compile_solidity tool...")
            compilation_result = agent_executor.invoke({"contract_code": contract_code}, tool="compile_solidity")
            pprint(f"Compilation result: {compilation_result}")

            # Analyze the contract with Slither
            pprint("Invoking analyze_with_slither tool...")
            slither_result = agent_executor.invoke({"contract_code": contract_code}, tool="analyze_with_slither")
            pprint(f"Slither analysis result: {slither_result}")

            # Save the contract and report
            pprint("Invoking save_contract_and_report tool...")
            save_result = agent_executor.invoke({
                "contract_code": contract_code,
                "slither_output": slither_result,
                "contract_filename": f"contract_{i+1}.sol",
                "report_filename": f"contract_{i+1}_slither_report.txt"
            }, tool="save_contract_and_report")
            pprint(f"Saving result: {save_result}")

            pprint(f"Contract {i+1} completed successfully")

        except Exception as e:
            logging.error(f"Error during agent execution for contract {i + 1}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run contract generation and validation using Cohere and LangChain.")
    parser.add_argument("-c", "--contracts", type=int, default=1, help="Number of contracts to generate and validate.")
    args = parser.parse_args()

    # Setup and run the ReAct agent
    setup_react_agent(args.contracts)
