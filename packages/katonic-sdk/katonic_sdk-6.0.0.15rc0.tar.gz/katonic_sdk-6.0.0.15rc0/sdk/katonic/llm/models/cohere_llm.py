#!/usr/bin/env python
# Script            : Main script for Cohere foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
import traceback
from langchain_community.chat_models import ChatCohere
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_cohere_model(service_type, model_name, logger=None):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        cohere_llm = ChatCohere(
        model=model_name,
        cohere_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        temperature=float(os.environ["TEMPERATURE"])
        if "TEMPERATURE" in os.environ
        else 0.3,
            # max_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else 256,
        )
        return cohere_llm
    except Exception as e:
        error_traceback = traceback.format_exc()
        error_message = "An error occurred. Traceback:\n" + error_traceback
        return str(e)
