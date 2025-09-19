#!/usr/bin/env python
# Script            : Main script for AI21 Foundation model.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
from langchain_community.llms import AI21
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_ai21_model(service_type, model_name, logger=None):
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    try:
        ai21_llm = AI21(
            model=model_name,
            ai21_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
            temperature=float(os.environ["TEMPERATURE"])
            if "TEMPERATURE" in os.environ
            else 0.3,
            maxTokens=int(os.environ["MAXTOKENS"])
            if "MAXTOKENS" in os.environ
            else 256,
            topP=float(os.environ["TOP_P"])
            if "TOP_P" in os.environ
            else 1.0,
        )
        return ai21_llm
    except Exception as e:
        return str(e)
