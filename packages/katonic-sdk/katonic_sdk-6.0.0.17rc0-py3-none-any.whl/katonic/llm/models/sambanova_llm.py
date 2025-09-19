#!/usr/bin/env python
# Script            : Build utils script for SambaNova llm
# Component         : GenAi Extraction Validate API
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------


import os
import json
import requests
from typing import Any, List, Mapping, Optional

from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo


class SambaNovaLLM(LLM):
    api_key: str
    model_name: str

    @property
    def _llm_type(self) -> str:
        return "SambaNova"
    

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        headers = {
            'Content-Type': 'application/json',
            'key': self.api_key,
            'modelName': self.model_name,
        }
        prompt = prompt.replace("\n", "")
        instance_str = """{{"conversation_id":"sambaverse-conversation-id","messages":[{{"message_id":0,"role":"user","content":"{}"}}]}}""".format(prompt)

        json_data = {
            "instance": instance_str,
            "params": {
                "do_sample": {
                    "type": "bool",
                    "value": "true",
                },
                "max_tokens_to_generate": {
                    "type": "int",
                    "value": str(os.environ["MAX_NEW_TOKENS"])
                    if "MAX_NEW_TOKENS" in os.environ
                    else "2000",
                },
                "process_prompt": {
                    "type": "bool",
                    "value": "true",
                },
                "repetition_penalty": {
                    "type": "float",
                    "value": "1.0",
                },
                "return_token_count_only": {
                    "type": "bool",
                    "value": "false",
                },
                "select_expert": {
                    "type": "str",
                    "value": "Mistral-7B-Instruct-v0.2",
                },
                "stop_sequences": {
                    "type": "str",
                    "value": "",
                },
                "temperature": {
                    "type": "float",
                    "value": str(os.environ["TEMPERATURE"])
                    if "TEMPERATURE" in os.environ
                    else "0.7",
                },
                "top_k": {
                    "type": "int",
                    "value": "50",
                },
                "top_p": {
                    "type": "float",
                    "value": "0.95",
                },
            },
        }


        output = requests.post('https://sambaverse.sambanova.ai/api/predict', headers=headers, json=json_data)
        if output.status_code == 200:
            api_response = output.text
            response_list = api_response.strip().split('\n')

            parsed_responses = []

            for response in response_list:
                cleaned_response = response.strip()
                if cleaned_response:
                    parsed_response = json.loads(cleaned_response)
                    parsed_responses.append(parsed_response)

            final_output = ""
            for response in parsed_responses:
                current_response = response["result"]["responses"][0]["stream_token"]
                final_output += current_response
            return final_output
        else:
            return output.text
            

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"api_key": self.api_key, "model_name": self.model_name}


def create_sambanova_model(service_type, model_name, logger):
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    api_key = decrypt_encryption_seed(fm_meta["apiKey"])


    katonic_llm = SambaNovaLLM(api_key=api_key, model_name=model_name)
    return katonic_llm