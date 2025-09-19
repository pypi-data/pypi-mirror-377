#!/usr/bin/env python
# Script            : Main script for Replicate Foundation model
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
import traceback
from langchain_community.llms import Replicate
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_replicate_model(service_type, model_name, logger):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        logger.info(
            "------------------ Started Replicate Completion ------------------"
        )
        os.environ["REPLICATE_API_TOKEN"] = decrypt_encryption_seed(os.environ["SEED"])
        replicate_llm = Replicate(
            model=model_name,
            replicate_api_token=decrypt_encryption_seed(fm_meta["apiKey"]),
            model_kwargs={
                "temperature": float(os.environ["TEMPERATURE"])
                if "TEMPERATURE" in os.environ
                else 0.3,
                "agree_to_research_only": True
                # "max_length": model_parameters["max_tokens"],
                # "top_p": model_parameters["top_p"],
                # "frequency_penalty": model_parameters["frequency_penalty"],
            },
        )
        return replicate_llm
    except Exception as e:
        error_traceback = traceback.format_exc()
        error_message = "An error occurred. Traceback:\n" + error_traceback
        logger.info(str(error_message))
        return str(e)
