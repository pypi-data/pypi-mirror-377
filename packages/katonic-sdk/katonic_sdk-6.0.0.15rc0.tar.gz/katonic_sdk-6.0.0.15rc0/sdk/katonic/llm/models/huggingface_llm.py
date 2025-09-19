#!/usr/bin/env python
# Script            : Main script for Huggingface undation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import requests
from typing import Any, List, Mapping, Optional

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

class HuggingfaceLLM(LLM):
    model_name: str
    api_key: str

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        inference_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

        payload = {
            "inputs": prompt,
        }
        response = requests.post(inference_url, json=payload, headers=headers)
        if response.status_code == 503:
            raise Exception(
    f"LLM Server: Error {response.status_code}, Huggingface has Deprecated the {self.model_name} model space or model is not available."
            )
        elif response.status_code >= 500:
            raise Exception(f"LLM Server: Error {response.status_code, response.text}")
        elif response.status_code >= 400:
            raise ValueError(f"LLM received an invalid payload/URL: {response.text}")
        elif response.status_code != 200:
            raise Exception(
    f"LLM returned an unexpected response with status "
    f"{response.status_code}: {response.text}"
            )
        return response.json()[0]["generated_text"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name, "api_key": self.api_key}

def create_huggingface_model(service_type, model_name, logger=None):
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    if len(fm_meta) > 0:
        api_key = decrypt_encryption_seed(fm_meta["apiKey"])

        huggingface_llm = HuggingfaceLLM(model_name=model_name, api_key=api_key)
        return huggingface_llm
    else:
        return "Oops!! Seems like the model has been deleted, Please contact the administrator."
