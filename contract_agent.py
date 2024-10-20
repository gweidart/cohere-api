# contract_agent.py

from langchain.agents import AgentExecutor
from rich.progress import Progress
import logging
from cohere_api import CohereAPI
from solidity_tools import SolidityValidator
from storage import ContractStorage

class ContractAgent(Agent):
    def __init__(self, cohere_tool, solidity_tool, slither_tool, storage_tool):
        self.cohere_tool = get_assignment_tool
        self.solidity_tool = solidity_tool
        self.slither_tool = slither_tool
        self.storage_tool = storage_tool

    def execute(self):
        with Progress() as progress:
            task = progress.add_task("[cyan]Executing contract generation and validation...", total=100)

            # Step 1: Generate the contract
            logging.info("Generating contract with Cohere")
            contract_text = self.cohere_tool.run()
            if not contract_text:
                logging.error("Contract generation failed.")
                return None
            progress.update(task, advance=30)

            # Step 2: Compile the contract
            logging.info("Compiling contract with Solidity compiler")
            compilation_result = self.solidity_tool.run()
            if "failed" in compilation_result:
                logging.error("Compilation failed.")
                return None
            progress.update(task, advance=30)

            # Step 3: Analyze the contract with Slither
            logging.info("Analyzing contract with Slither")
            slither_report = self.slither_tool.run()
            if not slither_report:
                logging.error("Slither analysis failed.")
                return None
            progress.update(task, advance=20)

            # Step 4: Save contract and report
            logging.info("Saving contract and Slither report")
            contract_name = f"contract_{self.cohere_tool.complexity}_{'_'.join(self.cohere_tool.vulnerabilities)}"
            self.storage_tool.save_contract(contract_text, self.cohere_tool.complexity, "vulnerabilities", contract_name)
            progress.update(task, advance=20)

            logging.info(f"Contract and Slither report saved as {contract_name}")
            return slither_report
