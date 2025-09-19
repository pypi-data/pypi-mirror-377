#!/usr/bin/env python
# Script            : Main script for AlephAlpha Foundation model
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import os
from langchain_community.llms import AlephAlpha
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_alephalpha_model(service_type, model_name, logger=None):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        aa_llm = AlephAlpha(
        model=model_name,
        stop_sequences=["Q:"],
        aleph_alpha_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        temperature=float(os.environ["TEMPERATURE"])
        if "TEMPERATURE" in os.environ
        else 0.3,
            # top_k=int(os.environ["TOP_K"])
            # if "TOP_K" in os.environ
            # else 0,
            # maximum_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else 64,
            # top_p=float(os.environ["TOP_P"])
            # if "TOP_P" in os.environ
            # else 0.0,
        )
        return aa_llm
    except Exception as e:
        return str(e)
