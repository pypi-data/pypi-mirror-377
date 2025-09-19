#!/usr/bin/env python
# Script            : Main script for TGI foundation models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import re
import requests
from ..logutils import handle_exception
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from langchain_openai import ChatOpenAI

mixtral_stop_config = ["[INST]", "[/INST]"]
dbrx_stop_config = ["<|im_start|>", "<|im_end|>"]
llama2_stop_config = ["[INST]", "[/INST]", "<<SYS>>", "<</SYS>>"]
llama3_stop_config = ["<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>", "<|im_end|>"]

stop_config_mapper = {
    "llama3-70b-instruct": llama3_stop_config,
    "llama2-70b-chat": llama2_stop_config,
    "mixtral-8x7b": mixtral_stop_config,
    "mixtral-8x22b": mixtral_stop_config,
    "dbrx": dbrx_stop_config,
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


def create_tgi_model(service_type, logger):
    logger.info("------------------ Started TGI Completion ------------------")
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        meta_dict = fm_meta["metadata"]
        api_endpoint = ensure_v1_in_url(meta_dict["apiRoute"])
        info_endpoint = api_endpoint.replace("/v1", "") + "info"
        logger.info(f"API detials info endpoint: {info_endpoint}")
        try:
            response = requests.get(info_endpoint)
            logger.info(response.text)
            model_name = response.json()["model_id"]
            stop_sequences = []
            if "Llama-3" in model_name:
                stop_sequences = stop_config_mapper["llama3-70b-instruct"]
            if "dbrx" in model_name:
                stop_sequences = stop_config_mapper["dbrx"]
            if "mixtral" in model_name:
                if "8x22b" in model_name:
                    stop_sequences = stop_config_mapper["mixtral-8x22b"]
                if "8x7b" in model_name:
                    stop_sequences = stop_config_mapper["mixtral-8x7b"]
                stop_sequences = stop_config_mapper["mixtral-8x22b"]
            max_total_tokens = response.json()["max_total_tokens"]
            max_total_tokens = int(max_total_tokens * 0.25)
        except Exception:
            error_traceback = handle_exception()
            err_msg = f"Failed to fetch TGI model info due to {error_traceback}"
            logger.info(err_msg)
            return err_msg
        tgi_api_key = "XXXXXXXXXXXX"
        tgi_llm = ChatOpenAI(
            base_url=api_endpoint,
            model_name=model_name,
            openai_api_key=tgi_api_key,
            max_tokens=max_total_tokens,
            model_kwargs={"stop":stop_sequences}
        )
        logger.info("LLM Created Successfully...")
        return tgi_llm
    except Exception as e:
        return str(e)
