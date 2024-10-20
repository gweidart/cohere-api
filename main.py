# main.py

import os
import argparse
from rich.progress import Progress
from rich.logging import RichHandler
import logging
from cohere_api import CohereAPI
from solidity_tools import SolidityValidator
from storage import ContractStorage
from utils import select_random_vulnerabilities, select_random_complexity
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.llms import Cohere  # Import the Cohere LLM class from LangChain

# Configure Rich logging
logging.basicConfig(
    level="INFO", format="%(message)s", handlers=[RichHandler()]
)

def setup_react_agent(num_contracts):
    # Get the API key from the environment variable
    api_key = os.getenv("COHERE_API_KEY")
    
    if not api_key:
        raise EnvironmentError("COHERE_API_KEY is not set in the environment. Please set it before running the script.")
    
    # Initialize Cohere LLM with the API key
    llm = Cohere(cohere_api_key=api_key)

    with Progress() as progress:
        task = progress.add_task("[cyan]Setting up agent...", total=100)

        # Load the Cohere API (our wrapper for contract generation)
        progress.update(task, advance=20)
        cohere_api = CohereAPI(api_key)

        # Loop to generate multiple contracts based on the argument -c
        for i in range(num_contracts):
            # Randomly select complexity and vulnerabilities for each contract
            complexity = select_random_complexity()
            vulnerabilities = select_random_vulnerabilities()

            # Define the Cohere tool for contract generation
            get_assignment_tool = Tool(
                name="Random Vulnerability assignment",
                func=lambda: cohere_api.generate_contract(complexity, vulnerabilities),
                description="Assigns a random mix of complexity and smart contract vulnerabilities for you to include when you generate Solidity smart contracts."
            )

            # Define Solidity compilation and Slither analysis tools
            solidity_tool = SolidityValidator("")
            tools = [
                Tool(
                    name="Compile Solidity",
                    func=solidity_tool.compile_contract,
                    description="Compiles the generated Solidity contract."
                ),
                Tool(
                    name="Run Slither Analysis",
                    func=solidity_tool.analyze_security,
                    description="Runs Slither security analysis on the compiled contract."
                )
            ]

            # Initialize the LangChain ReAct agent with the tools and the LLM
            agent = initialize_agent(
                tools=[get_assignment_tool, *tools],  # Add all tools to the agent
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Correct ReAct framework for tool selection
                llm=llm,  # Pass the Cohere LLM into the agent
                verbose=True
            )

            # Define the input task for the agent
            input_task = f"Generate Solidity contract #{i+1} with vulnerabilities, compile it, and run a security analysis."

            # Execute the agent workflow with the input task
            progress.update(task, advance=30)
            agent.run(input_task)  # Pass the input task description to the agent

            progress.update(task, advance=50)

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate and validate Solidity contracts.")
    parser.add_argument("-c", "--contracts", type=int, default=1, help="Number of contracts to generate (default: 1)")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the number of contracts passed as an argument
    setup_react_agent(args.contracts)
