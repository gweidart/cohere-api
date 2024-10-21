import os
import argparse
from rich.logging import RichHandler
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere, create_cohere_react_agent
from langchain.agents import AgentExecutor
from cohere_api import CohereAPI
from solidity_tools import SolidityValidator
from storage import ContractStorage
from utils import select_random_vulnerabilities, load_prompt_from_file
from langchain.tools import Tool

# Configure Rich logging
logging.basicConfig(
    level="INFO", format="%(message)s", handlers=[RichHandler()]
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
        func=lambda _: {"complexity": select_random_complexity(), "vulnerabilities": select_random_vulnerabilities()},
        description="Selects random contract complexity and vulnerabilities."
    )

    def generate_contract_tool(params):
        if not isinstance(params, dict):
            raise TypeError("Expected params to be a dictionary but got: " + str(type(params)))
        complexity = params["complexity"]
        vulnerabilities = params["vulnerabilities"]
        logging.info(f"Generating contract with Complexity: {complexity}, Vulnerabilities: {vulnerabilities}")
        return cohere_llm.generate_contract(complexity, vulnerabilities)


    contract_generation_tool = Tool(
        name="Generate Solidity Contract",
        func=generate_contract_tool,
        description="Generates a Solidity contract using the Cohere model."
    )

    compile_contract_tool = Tool(
        name="Compile Solidity Contract",
        func=lambda contract_text: SolidityValidator(contract_text).compile_contract(),
        description="Compiles the generated Solidity contract using the Solidity compiler."
    )

    analyze_contract_tool = Tool(
        name="Analyze Solidity Contract",
        func=lambda contract_text: SolidityValidator(contract_text).analyze_security(f"contract_analysis"),
        description="Analyzes the compiled Solidity contract for vulnerabilities using Slither."
    )

    save_to_file_tool = Tool(
        name="Save Contract and Report",
        func=lambda contract_text: save_contract_and_report(contract_text, "contract_analysis", "random_complexity", "vulnerable"),
        description="Saves the generated contract and its report."
    )

    # Use create_cohere_react_agent to assemble the ReAct agent with tools
    prompt = ChatPromptTemplate.from_template("{text}")
    load_preamble = load_prompt_from_file()
    preamble = load_preamble
    initial_input = {"input": "Start contract generation process"}
    tools = [parameter_selection_tool, contract_generation_tool, compile_contract_tool, analyze_contract_tool, save_to_file_tool]
    react_agent = create_cohere_react_agent(llm=cohere_llm, tools=tools, prompt=initial_input)

    # Execute the agent for each contract to generate
    for _ in range(num_contracts):
        agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)
        agent_executor.invoke(input=initial_input, preamble=preamble)

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
