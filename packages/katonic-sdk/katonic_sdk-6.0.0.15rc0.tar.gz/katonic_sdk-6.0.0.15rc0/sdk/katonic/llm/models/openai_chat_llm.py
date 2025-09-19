#!/usr/bin/env python
# Script            : Main script for AnyScale foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.
import os
from ..utilities.utils import decrypt_encryption_seed
from langchain_openai import ChatOpenAI
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_openai_model(service_type, model_name, logger=None):
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    try:
        temperature=0.3
        if "o3" in model_name or "o4-mini" in model_name:
            temperature = 1
        api_key = fm_meta["apiKey"]
        openai_llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=None,
            openai_api_key=decrypt_encryption_seed(api_key) if api_key else "",
            streaming=True
        )
        return openai_llm
        
    except Exception as e:
        return str(e)
