#!/usr/bin/env python
# Script            : Main script for Nvidia foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.
import os
import traceback
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from langchain_nvidia_ai_endpoints import ChatNVIDIA

def create_nvidia_model(service_type, model_name, logger=None):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        os.environ["NVIDIA_API_KEY"] = decrypt_encryption_seed(fm_meta["apiKey"])
        nvidia_llm = ChatNVIDIA(
        model=model_name,
        temperature=float(os.environ["TEMPERATURE"])
        if "TEMPERATURE" in os.environ
        else 0.7,
            # max_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else None,
        )
        return nvidia_llm
    except Exception:
        # Log the traceback without exposing sensitive information
        error_traceback = traceback.format_exc()
        error_message = "An error occurred. Traceback:\n" + error_traceback
        return str(error_message)