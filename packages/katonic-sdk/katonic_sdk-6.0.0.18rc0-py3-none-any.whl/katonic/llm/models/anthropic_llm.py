#!/usr/bin/env python
# Script            : Main script for Anthropic Foundation model
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

from langchain_anthropic.chat_models import ChatAnthropic
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_anthropic_model(service_type, model_name, logger=None):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        anthropic_llm = ChatAnthropic(
            # streaming=True,
            # callbacks=[callback_handler],
        model_name=model_name,
        anthropic_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        )
        return anthropic_llm
    except Exception as e:
        return str(e)

