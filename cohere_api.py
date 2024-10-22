# cohere_api.py

import cohere
import logging
from utils import load_prompt_from_file
from requests.exceptions import RequestException  # For catching HTTP-related errors
from rich.pretty import pprint
from rich.progress import Progress

class CohereAPI:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
        self.base_prompt = load_prompt_from_file()  # Load the base prompt from file
    
    def generate_contract(self, complexity, vulnerabilities):
        """Generates a Solidity contract with specified complexity and vulnerabilities."""
        try:
            if not isinstance(vulnerabilities, list):
                raise ValueError(f"Expected a list of vulnerabilities, got {type(vulnerabilities)}")

            # Construct the prompt for contract generation
            vulnerability_prompt = f"Generate a Solidity contract with the following vulnerabilities: {', '.join(vulnerabilities)}."
            full_prompt = f"{self.base_prompt}\n\nComplexity level: {complexity}\n{vulnerability_prompt}"

                        # Add progress tracking
            with Progress() as progress:
                response = self.client.generate(
                    model='command-r-plus-08-2024',
                    prompt=full_prompt,
                    max_tokens=3900,
                    temperature=0.3,
                    stop_sequences=["END"],
                    return_likelihoods="NONE"
                )
            contract_code = response.generations[0].text
            return contract_code

        except RequestException as e:
            logging.error(f"Network error while generating contract: {e}")
            return None
        except Exception as e:
            logging.error(f"An error occurred while generating contract: {e}")
            return None
