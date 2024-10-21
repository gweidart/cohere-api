# cohere_api.py

import cohere
import logging
from utils import load_prompt_from_file
from rich.progress import Progress
from requests.exceptions import RequestException  # For catching HTTP-related errors

class CohereAPI:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
        self.base_prompt = load_prompt_from_file()  # Load the base prompt from file
    
    def generate_contract(self, complexity, vulnerabilities):
        """Generates a Solidity contract with specified complexity and vulnerabilities."""
        try:
            vulnerability_prompt = f"Generate a Solidity contract with the following vulnerabilities: {', '.join(vulnerabilities)}."
            full_prompt = f"{self.base_prompt}\n\nComplexity level: {complexity}\n{vulnerability_prompt}"

            # Add progress tracking
            with Progress() as progress:
                task = progress.add_task("[green]Generating contract...", total=100)
                response = self.client.generate(
                    model='command-r-plus-08-2024',
                    prompt=full_prompt,
                    max_tokens=500,
                    temperature=0.7,
                    stop_sequences=["END"],
                    return_likelihoods="NONE"
                )
                progress.update(task, advance=100)

            contract_text = response.generations[0].text
            return contract_text
        
        # Catch HTTP errors (if using requests underneath) and generic exceptions
        except RequestException as e:
            logging.error(f"Network error while generating contract: {e}")
            return None
        except Exception as e:
            logging.error(f"An error occurred while generating contract: {e}")
            return None
