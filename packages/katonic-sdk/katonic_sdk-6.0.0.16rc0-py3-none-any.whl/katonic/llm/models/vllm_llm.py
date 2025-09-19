#!/usr/bin/env python
# Script            : Main script for VLLM foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import re
from openai import OpenAI

from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from langchain_openai import ChatOpenAI


mixtral_stop_config = ["[INST]", "[/INST]"]
dbrx_stop_config = ["<|im_start|>", "<|im_end|>"]
llama2_stop_config = ["[INST]", "[/INST]", "<<SYS>>", "<</SYS>>"]
llama3_stop_config = [
    "<|start_header_id|>",
    "<|end_header_id|>",
    "<|eot_id|>",
    "<|im_end|>",
]
Meta_Llama_3_8B = ["<|im_end|>"]


stop_config_mapper = {
    "llama3-70b-instruct": llama3_stop_config,
    "llama2-70b-chat": llama2_stop_config,
    "mixtral-8x7b": mixtral_stop_config,
    "mixtral-8x22b": mixtral_stop_config,
    "dbrx": dbrx_stop_config,
    "meta-llama/Meta-Llama-3-8B": Meta_Llama_3_8B,
}


def ensure_v1_in_url(url):
    match = re.match(r"(https?://[^/]+)(/[^/]*)", url)

    if match:
        base_url = match.group(1)
        path = match.group(2)

        if "/v1" not in path:
            return f"{base_url}/v1/"
        else:
            truncated_path = path.split("/v1")[0] + "/v1"
            return f"{base_url}{truncated_path}/"
    else:
        return url


def create_vllm_model(service_type, logger):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        meta_dict = fm_meta["metadata"]
        api_endpoint = ensure_v1_in_url(meta_dict["apiRoute"])
        vllm_api_key = "XXXXXXXXXXXX"
        client = OpenAI(
            api_key=vllm_api_key,
            base_url=api_endpoint,
        )

        models = client.models.list()
        model = models.data[0].id
        max_model_length = models.data[0].max_model_len
        max_total_tokens = int(max_model_length * 0.25)
        stop_sequences = []
        if "Llama-3" in model:
            stop_sequences = stop_config_mapper["llama3-70b-instruct"]
        if "dbrx" in model:
            stop_sequences = stop_config_mapper["dbrx"]
        if "meta-llama/Meta-Llama-3-8B" in model:
            stop_sequences = stop_config_mapper["meta-llama/Meta-Llama-3-8B"]
        if "mixtral" in model:
            if "8x22b" in model:
                stop_sequences = stop_config_mapper["mixtral-8x22b"]
            if "8x7b" in model:
                stop_sequences = stop_config_mapper["mixtral-8x7b"]
            stop_sequences = stop_config_mapper["mixtral-8x22b"]

        vllm_llm = ChatOpenAI(
            base_url=api_endpoint,
            model_name=model,
            openai_api_key=vllm_api_key,
            max_tokens=max_total_tokens,
            stop=stop_sequences,
        )
        return vllm_llm
    except Exception as e:
        return str(e)
