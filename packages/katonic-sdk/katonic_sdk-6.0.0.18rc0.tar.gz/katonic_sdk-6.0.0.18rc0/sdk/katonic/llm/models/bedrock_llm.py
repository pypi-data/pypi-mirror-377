import os
import json
import boto3
import httpx
from typing import Any, List, Mapping, Optional

from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun


class BedrockError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        self.request = httpx.Request(
            method="POST",
            url="https://bedrock-runtime.us-west-2.amazonaws.com"  # More accurate than console URL
        )
        self.response = httpx.Response(status_code=status_code, request=self.request)
        super().__init__(self.message)


class BedrockLLM(LLM):
    params: dict
    model_name: str

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

        aws_access_key_id = self.params["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = self.params["AWS_SECRET_ACCESS_KEY"]
        region_name = self.params["AWS_REGION_NAME"]
        endpoint_url = f"https://bedrock-runtime.{region_name}.amazonaws.com"

        client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )

        accept = "application/json"
        content_type = "application/json"
        payload = json.dumps({"prompt": prompt})

        try:
            response = client.invoke_model(
                body=payload,
                modelId=self.model_name,
                accept=accept,
                contentType=content_type,
            )
            response_body = json.loads(response.get("body").read())

            if "ai21" in self.model_name:
                return response_body.get("completions")[0].get("data").get("text")
            elif "anthropic" in self.model_name:
                return response_body["completion"]
            elif "cohere" in self.model_name:
                return response_body["generations"][0]["text"]
            elif "meta" in self.model_name:
                return response_body["generation"]
            else:  # amazon titan
                return response_body.get("results")[0].get("outputText")

        except Exception as e:
            raise BedrockError(status_code=500, message=str(e))

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"params": self.params, "model_name": self.model_name}


def create_bedrock_model(service_type: str, model_name: str, logger=None) -> BedrockLLM:
    try:
        params = {
            "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
            "AWS_REGION_NAME": os.environ["AWS_REGION_NAME"],
        }
        bedrock_llm = BedrockLLM(params=params, model_name=model_name)
        return bedrock_llm
    except KeyError as e:
        raise BedrockError(status_code=401, message=f"Missing AWS credential: {e}")