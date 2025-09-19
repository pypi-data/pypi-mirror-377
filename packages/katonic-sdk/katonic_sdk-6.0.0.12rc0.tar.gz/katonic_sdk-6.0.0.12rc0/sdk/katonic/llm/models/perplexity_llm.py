#!/usr/bin/env python
# Script            : Main script for Perplexity foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
import traceback
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from langchain_openai import ChatOpenAI


def create_perplexity_model(service_type, model_name, logger):
    logger.info("------------------ Started Perplexity Completion ------------------")
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        perplexity_llm = ChatOpenAI(
            base_url="https://api.perplexity.ai",
            model_name=model_name,
            temperature=(
                float(os.environ["TEMPERATURE"]) if "TEMPERATURE" in os.environ else 0.7
            ),
            # max_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else None,
            openai_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        )
        logger.info("LLM Created Successfully...")
        return perplexity_llm
    except Exception:
        # Log the traceback without exposing sensitive information

        error_traceback = traceback.format_exc()
        traceback_lines = error_traceback.splitlines()
        error_traceback = traceback_lines[-1]
        error_message = "An error occurred. Traceback:\n" + error_traceback
        logger.info(str(error_message))
        return str(error_message)