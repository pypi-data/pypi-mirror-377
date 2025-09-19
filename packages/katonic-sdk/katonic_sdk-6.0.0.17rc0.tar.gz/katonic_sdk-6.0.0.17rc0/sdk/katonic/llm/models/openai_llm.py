#!/usr/bin/env python
# Script            : Main script for OpenAI model.
# Component         : GenAi model deployment
# Author            : Anuja Fole
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.
import os
from ..utilities.utils import decrypt_encryption_seed
from langchain_openai import ChatOpenAI,OpenAI

def get_model_and_api():
    general_settings = get_general_settings()
    model = general_settings["modelConfig"]["genaiWorkplaceAssistant"]["primaryModel"]["modelName"]
    api_key = general_settings["modelConfig"]["genaiWorkplaceAssistant"]["primaryModel"]["apiKey"]
    return model, api_key

def get_openai_summary():
    model, api_key = get_model_and_api()
    model = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    temperature=0.3,
    max_tokens=100,
    openai_api_key=os.environ["OPENAI_TOKEN"],
    )

    return model

def get_search_summary_model():
    model = ChatOpenAI(
    model="gpt-4-0125-preview",
    temperature=0.3,
    openai_api_key=os.environ["OPENAI_TOKEN"],
    stream=True
    )

    return model

def get_ques_validaton_model():
    model = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=100,
    openai_api_key=os.environ["OPENAI_TOKEN"]) 
    return model  