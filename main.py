import os
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
from utils import load_preamble_from_file

# Configure Rich logging
logging.basicConfig(
    level="INFO", format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)

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
    tools = [compile_solidity, analyze_with_slither, save_contract_and_report, assess_complexity_and_vulnerabilities]
    prompt = ChatPromptTemplate.from_messages(chat_hx)
    react_agent = create_cohere_react_agent(llm=cohere_llm, tools=tools, prompt=prompt)

    # Execute the agent for each contract to generate
    for _ in range(num_contracts):
        agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)
        agent_executor.invoke({"preamble": preamble})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run contract generation and validation using Cohere and LangChain.")
    parser.add_argument("-c", "--contracts", type=int, default=1, help="Number of contracts to generate and validate.")
    args = parser.parse_args()

    # Setup and run the ReAct agent
    setup_react_agent(args.contracts)
