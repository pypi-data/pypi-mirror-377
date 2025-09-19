#!/usr/bin/env python
# Script            : Main script for AnyScale foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
from langchain_together import ChatTogether
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo


def create_togetherai_model(service_type, model_name, logger):
    logger.info("------------------ Started Together AI Completion ------------------")

    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        together_llm = ChatTogether(
            model=model_name,
            temperature=float(os.environ["TEMPERATURE"])
            if "TEMPERATURE" in os.environ
            else 0.3,
            # max_tokens=int(os.environ["MAX_TOKENS"]),
            # model_kwargs={
            #     "top_p": float(os.environ["TOP_P"])
            # },  # Use float for non-integer values
            # n=int(os.environ["TOP_K"]),
            together_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        )
        return together_llm
    except Exception as e:
        return str(e)
