#!/usr/bin/env python
# Script              : Main script for model deployment
# Component           : GenAi model deployment
# Author              : Vinay Namani
# Copyright (c)       : 2025 Katonic Pty Ltd. All rights reserved.
import requests
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def process_vision_request(image, query, model_id, model_name,logger):
    fm_meta = retrieve_model_metadata_from_mongo(model_id)
    api_key = decrypt_encryption_seed(fm_meta["apiKey"])
    source = image
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": source}},
                ],
            }
        ],
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    if response.status_code != 200:
        output = response.json()
        return output["error"]["message"]
    else:
        output = response.json()["choices"][0]["message"]["content"]
        return output

def vision_completion(image, query, model_id, model_name, logger):
    """
    Alias for process_vision_request to maintain compatibility with FastAPI router code.
    """
    return process_vision_request(image, query, model_id, model_name, logger)
