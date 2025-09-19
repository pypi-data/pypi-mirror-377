#!/usr/bin/env python
# Script            : Main script for AnyScale foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
from langchain_community.chat_models import ChatAnyscale
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_anyscale_model(service_type, model_name, logger):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        logger.info("------------------ Started AnyScale Completion ------------------")
        anyscale_llm = ChatAnyscale(
            model=model_name,
            anyscale_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
            temperature=float(os.environ["TEMPERATURE"])
            if "TEMPERATURE" in os.environ
            else 0.3,
            # max_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else 128
        )
        return anyscale_llm
    except Exception as e:
        return str(e)
