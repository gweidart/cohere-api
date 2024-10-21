import os
import random
import argparse
from rich.logging import RichHandler
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_cohere import ChatCohere, create_cohere_react_agent
from langchain.agents import AgentExecutor
from cohere_api import CohereAPI
from solidity_tools import *
from storage import ContractStorage
from utils import VULNERABILITIES, COMPLEXITY, load_preamble_from_file
from langchain.tools import Tool

# Configure Rich logging
logging.basicConfig(
    level="ERROR", format="%(message)s", handlers=[RichHandler()]
)

def setup_react_agent(num_contracts):
    # Get the API key from the environment variable
    api_key = os.getenv("COHERE_API_KEY")
    
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY is not set in the environment. Please set it before running the script.")
    
    # Initialize Cohere LLM with the API key for ReAct agent
    cohere_llm = ChatCohere(cohere_api_key=api_key, model="command-r-plus-08-2024")

    # Define tools for the agent based on the task requirements
    parameter_selection_tool = Tool(
        name="Select Complexity and Vulnerabilities",
        func=lambda _: {"complexity": complexity, "vulnerabilities": vuln_str},
        description="Selects random contract complexity and vulnerabilities."
    )

    compile_contract_tool = Tool(
        name="Compile Solidity Contract",
        func=lambda contract_code: (contract_code),
        description="Compiles the generated Solidity contract using the Solidity compiler."
    )

    analyze_contract_tool = Tool(
        name="Analyze Solidity Contract",
        func=lambda contract_code: analyze_with_slither(contract_code),
        description="Analyzes the compiled Solidity contract for vulnerabilities using Slither."
    )

    save_to_file_tool = Tool(
        name="Save Contract and Report",
        func=lambda contract_code: save_contract_and_report(contract_code, "contract_analysis", "random_complexity", "vulnerable"),
        description="Saves the generated contract and its report."
    )

    # Use create_cohere_react_agent to assemble the ReAct agent with tools
    complexity = random.choice(COMPLEXITY)
    # Randomly select 1-5 unique vulnerabilities
    vulnerabilities = random.sample(VULNERABILITIES, k=random.randint(1, 5))
    vuln_str = ', '.join(vulnerabilities)
    chat_hx = [SystemMessage(content="")
    ]
    load_preamble = load_preamble_from_file()
    preamble = load_preamble
    tools = [parameter_selection_tool, compile_contract_tool, analyze_contract_tool, save_to_file_tool]
    prompt = ChatPromptTemplate.from_messages(chat_hx)
    react_agent = create_cohere_react_agent(llm=cohere_llm, tools=tools, prompt=prompt)

    # Execute the agent for each contract to generate
    for _ in range(num_contracts):
        agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)
        agent_executor.invoke({"preamble": preamble})

def save_contract_and_report(contract_text, slither_report, complexity, vulnerabilities):
    """
    This function saves the generated contract and Slither report to appropriate files.
    """
    contract_storage = ContractStorage()  # Initialize the storage tool
    contract_name = f"contract_{complexity}_{'_'.join(vulnerabilities)}"

    # Save the contract
    contract_storage.save_contract(contract_text, complexity, "vulnerable", contract_name)

    logging.info(f"Contract and report saved as {contract_name}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run contract generation and validation using Cohere and LangChain.")
    parser.add_argument("-c", "--contracts", type=int, default=1, help="Number of contracts to generate and validate.")
    args = parser.parse_args()

    # Setup and run the ReAct agent
    setup_react_agent(args.contracts)
