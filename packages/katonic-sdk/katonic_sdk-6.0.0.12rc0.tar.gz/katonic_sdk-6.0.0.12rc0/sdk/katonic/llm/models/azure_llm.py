#!/usr/bin/env python
# Script            : Main script for Azure OpenAi models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
from langchain_openai import AzureChatOpenAI
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo


def create_azure_model(service_type, logger):
    logger.info(
        "------------------ Started  Azure X Openai Completion ------------------"
    )
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    meta_dict =  fm_meta['metadata']
    azure_llm = AzureChatOpenAI(
        openai_api_type="azure",
        api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        azure_endpoint=meta_dict["azureOpenaiBase"],
        azure_deployment=meta_dict["azureDeploymentName"],
        openai_api_version=meta_dict["azureOpenaiVersion"],
        temperature=float(os.environ["TEMPERATURE"])
        if "TEMPERATURE" in os.environ
        else 0.3,
        # max_tokens=int(os.environ["MAXTOKENS"])
        # if "MAXTOKENS" in os.environ
        # else 350,
    )
    return azure_llm
