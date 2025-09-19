import os
import requests
from typing import Any, List, Mapping, Optional

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from models.vllm_llm import create_vllm_model


class CustomLLM(LLM):
    api_endpoint: str

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
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": float(os.environ["TEMPERATURE"])
                if "TEMPERATURE" in os.environ
                else 0.3,
            },
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self.api_endpoint, json=payload, verify=False, headers=headers
        )
        if response.status_code >= 500:
            raise Exception(f"LLM Server: Error {response.status_code}")
        elif response.status_code >= 400:
            raise ValueError(f"LLM received an invalid payload/URL: {response.text}")
        elif response.status_code != 200:
            raise Exception(
                f"LLM returned an unexpected response with status "
                f"{response.status_code}: {response.text}"
            )
        return response.json()["generated_text"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"api_endpoint": self.api_endpoint}


def create_katonic_model(service_type, logger, model_name, module=None):
    model_meta = retrieve_model_metadata_from_mongo(service_type)
    project_name = model_meta["metadata"]["projectName"]
    api_endpoint = model_meta["metadata"]["apiRoute"]
    framework = model_meta["metadata"]["chatFramework"]

    logger.info(f"Model Name: {model_name}, Project Name: {project_name}")
    if len(retrieve_model_metadata_from_mongo(service_type)) > 0:
        logger.info("Started Katonic LLM")
        framework = framework.lower()
        if framework in ["tgi", "cog"]:
            logger.info("LLM Creation started for TGI and COG...")
            katonic_llm = CustomLLM(api_endpoint=api_endpoint)
        elif framework == "vllm":
            logger.info("LLM Creation started for VLLM...")
            katonic_llm = create_vllm_model(service_type=service_type, logger=logger)

        return katonic_llm
    else:
        return "Oops!! Seems like the model has been deleted, Please contact the administrator."
