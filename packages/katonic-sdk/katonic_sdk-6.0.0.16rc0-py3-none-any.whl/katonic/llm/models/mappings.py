#!/usr/bin/env python
# Script            : Maps the models with their screen names.
# Component         : Ace Primary Model Selection
# Author            : Anuja Fole
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

from typing import List, Dict
### LLM Models

openai_models: Dict = {
    "Openai/GPT-3.5-turbo-4k": "gpt-3.5-turbo",
    "Openai/GPT-3.5-turbo-16k": "gpt-3.5-turbo-16k",
    "Openai/gpt-3.5-turbo": "gpt-3.5-turbo",
    "Openai/gpt-3.5-turbo-1106": "gpt-3.5-turbo-1106",
    "Openai/gpt-4-turbo": "gpt-4-turbo",
    "Openai/gpt-4-8k": "gpt-4",
    "Openai/gpt-4-32k": "gpt-4-32k",
    "Openai/gpt-4-1106-preview": "gpt-4-1106-preview",
    "Openai/gpt-4-0125-preview": "gpt-4-0125-preview",
    "Openai/gpt-4o": "gpt-4o",
}

ollama_models: Dict = {"llama2:13b-chat": "llama2:13b-chat"}

openrouter_models: Dict = {
    "mistralai/mixtral-8x22b-instruct": "mistralai/mixtral-8x22b-instruct",
    "mistralai/mixtral-8x22b": "mistralai/mixtral-8x22b",
    "databricks/dbrx-instruct:nitro": "databricks/dbrx-instruct:nitro",
    "databricks/dbrx-instruct": "databricks/dbrx-instruct",
    "cohere/command-r-plus": "cohere/command-r-plus",
    "meta-llama/llama-3-8b-instruct": "meta-llama/llama-3-8b-instruct",
    "meta-llama/llama-3-70b-instruct": "meta-llama/llama-3-70b-instruct",
}

# openai_models: Dict = {
#     "Openai/gpt-3.5-turbo": "gpt-3.5-turbo",
#     "Openai/gpt-3.5-turbo-1106": "gpt-3.5-turbo-1106",
#     "Openai/gpt-4-8k": "gpt-4",
#     "Openai/gpt-4-32k": "gpt-4-32k",
#     "Openai/gpt-4-1106-preview": "gpt-4-1106-preview",
#     "Openai/gpt-4-0125-preview": "gpt-4-0125-preview",
# }

# from langchain.llms import Anyscale

anyscale_models: Dict = {
    "Anyscale/Llama-2-7b-chat-hf": "meta-llama/Llama-2-7b-chat-hf",
    "Anyscale/Llama-2-13b-chat-hf": "meta-llama/Llama-2-13b-chat-hf",
    "Anyscale/Llama-2-70b-chat-hf": "meta-llama/Llama-2-70b-chat-hf",
    "Anyscale/CodeLlama-34b-Instruct-hf": "codellama/CodeLlama-34b-Instruct-hf",
    "Anyscale/Mixtral-8x7B-Instruct-v0.1": "mistralai/Mixtral-8x7B-Instruct-v0.1",
}

# from langchain.llms import AzureOpenAI

azure_models: Dict = {
    "Azure/gpt-4": "azure-gpt4-8k",
    "Azure/gpt-4-32k": "azure-gpt4-32k",
    "Azure/gpt-35-turbo": "azure-gpt3.5-4k",
    "Azure/gpt-35-turbo-16k": "azure-gpt3.5-16k",
    "Azure/gpt-35-turbo-instruct": "azure-gpt35-turbo-insturct",
}

huggingface_models: Dict = {
    "Huggingface/Llama-2-7b-hf": "meta-llama/Llama-2-7b-hf",
    "Huggingface/Llama-2-7b-chat-hf": "meta-llama/Llama-2-7b-chat-hf",
    "Huggingface/Llama-2-13b-hf": "meta-llama/Llama-2-13b-hf",
    "Huggingface/Llama-2-13b-chat-hf": "meta-llama/Llama-2-13b-chat-hf",
    "Huggingface/Llama-2-70b-hf": "meta-llama/Llama-2-70b-hf",
    "Huggingface/Llama-2-70b-chat-hf": "meta-llama/Llama-2-70b-chat-hf",
    "Huggingface/falcon-7b-instruct": "tiiuae/falcon-7b-instruct",
    "Huggingface/CodeLlama-34b-Instruct-hf": "codellama/CodeLlama-34b-Instruct-hf",
    "Huggingface/Mixtral-8x7B-v0.1": "mistralai/Mixtral-8x7B-v0.1",
    "Huggingface/zephyr-7b-beta": "HuggingFaceH4/zephyr-7b-beta",
    "Huggingface/Mistral-7B-v0.1": "mistralai/Mistral-7B-v0.1",
}

# from langchain.llms import AI21

ai21_models: Dict = {
    "Ai21/J2-Mid": "j2-mid",
    "Ai21/J2-Ultra": "j2-ultra",
}

replicate_models: Dict = {
    "Replicate/llama-2-70b-chat": "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
    "Replicate/llama-2-13b-chat": "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d",
    "Replicate/vicuna-13b": "replicate/vicuna-13b:6282abe6a492de4145d7bb601023762212f9ddbbe78278bd6771c8b3b2f2a13b",
    "Replicate/flan-t5-large": "daanelson/flan-t5-large:ce962b3f6792a57074a601d3979db5839697add2e4e02696b3ced4c022d4767f",
    "Replicate/nateraw/nous-hermes-2-solar-10.7b": "nateraw/nous-hermes-2-solar-10.7b:1e918ab6ffd5872c21fba21a511f344fd12ac0edff6302c9cd260395c7707ff4",
}

# from langchain.llms import Cohere

cohere_models: Dict = {
    "Cohere/command": "command",
    "Cohere/command-light": "command-light",
    "Cohere/command-nightly": "command-nightly",
    "Cohere/command-light-nightly": "command-light-nightly",
    "Cohere/command-r": "command-r",
}

# from langchain.llms import AlephAlpha

aleph_alpha_models: Dict = {
    "Aleph Alpha/Luminous-base": "luminous-base",
    "Aleph Alpha/Luminous-base-control": "luminous-base-control",
    "Aleph Alpha/Luminous-supreme": "luminous-supreme",
    "Aleph Alpha/Luminous-supreme-control": "luminous-supreme-control",
    "Aleph Alpha/Luminous-extended": "luminous-extended",
    "Aleph Alpha/Luminous-extended-control": "luminous-extended-control",
}

# from langchain.llms import Anthropic

anthropic_models: Dict = {
    "Anthropic/claude-instant-1.2": "claude-instant-1.2",
    "Anthropic/claude-2": "claude-2.0",
    "Anthropic/claude-3-opus-20240229": "claude-3-opus-20240229",
    "Anthropic/claude-3-sonnet-20240229": "claude-3-sonnet-20240229",
    "Anthropic/claude-3-haiku-20240307": "claude-3-haiku-20240307",
}

togetherai_models: Dict = {
    "Together/llama-2-70b": "togethercomputer/llama-2-70b",
    "Together/llama-2-70b-chat": "togethercomputer/llama-2-70b-chat",
    "Together/Llama-2-7B-32K-Instruct": "togethercomputer/Llama-2-7B-32K-Instruct",
    "Together/RedPajama-INCITE-7B-Chat": "togethercomputer/RedPajama-INCITE-7B-Chat",
    "Together/RedPajama-INCITE-7B-Instruct": "togethercomputer/RedPajama-INCITE-7B-Instruct",
    "Together/Mistral-7B-Instruct-v0.1": "mistralai/Mistral-7B-Instruct-v0.1",
    "Together/Platypus2-70B-instruct": "garage-bAInd/Platypus2-70B-instruct",
    "Qwen/Qwen1.5-0.5B-Chat": "Qwen/Qwen1.5-0.5B-Chat",
    "Qwen/Qwen1.5-1.8B-Chat": "Qwen/Qwen1.5-1.8B-Chat",
    "Qwen/Qwen1.5-4B-Chat": "Qwen/Qwen1.5-4B-Chat",
    "Qwen/Qwen1.5-7B-Chat": "Qwen/Qwen1.5-7B-Chat",
    "Qwen/Qwen1.5-14B-Chat": "Qwen/Qwen1.5-14B-Chat",
    "Qwen/Qwen1.5-72B-Chat": "Qwen/Qwen1.5-72B-Chat",
    "Qwen/Qwen1.5-0.5B": "Qwen/Qwen1.5-0.5B",
    "Qwen/Qwen1.5-1.8B": "Qwen/Qwen1.5-1.8B",
    "Qwen/Qwen1.5-4B": "Qwen/Qwen1.5-4B",
    "Qwen/Qwen1.5-7B": "Qwen/Qwen1.5-7B",
    "Qwen/Qwen1.5-14B": "Qwen/Qwen1.5-14B",
    "Qwen/Qwen1.5-72B": "Qwen/Qwen1.5-72B",
}

groq_models = {
    "LLaMA2-70b": "llama2-70b-4096",  # Assuming no value specified for this key
    "Mixtral-8x7b": "mixtral-8x7b-32768",
    "Gemma-7b-it": "gemma-7b-it",
    "Llama-3-8B": "llama3-8b-8192",
    "Llama-3-70B": "llama3-70b-8192",
}

aws_bedrock_models = {
    "amazon.titan-text-express-v1": "amazon.titan-text-express-v1",
    "amazon.titan-text-lite-v1": "amazon.titan-text-lite-v1",
    "ai21.j2-ultra-v1": "ai21.j2-ultra-v1",
    "ai21.j2-mid-v1": "ai21.j2-mid-v1",
    "anthropic.claude-instant-v1": "anthropic.claude-instant-v1",
    "anthropic.claude-v2": "anthropic.claude-v2",
    "anthropic.claude-v1": "anthropic.claude-v1",
    "cohere.command-text-v14": "cohere.command-text-v14",
    "cohere.command-light-text-v14": "cohere.command-light-text-v14",
    "meta.llama2-13b-chat-v1": "meta.llama2-13b-chat-v1",
    "meta.llama2-70b-chat-v1": "meta.llama2-70b-chat-v1",
}

lighton_models = [
    "lightonai/RITA_s",
    "lightonai/RITA_m",
    "lightonai/RITA_l",
    "lightonai/RITA_xl",
]

google_models: Dict = {
    "Google/text-bison-001": "models/text-bison-001",
    "Google/gemini-pro": "gemini-pro",
}

### Embedding Models

openai_embedding_models = [
    "Openai/text-embedding-ada-002",
    "Openai/text-embedding-3-large",
    "Openai/text-embedding-3-small",
]
azure_embedding_models = ["Azure/text-embedding-ada-002"]
katonic_embedding_models = ["katonic_embedding"]
ollama_embedding_models = ["nomic-embed-text"]
replicate_embedding_models = {
    "Replicate/nateraw/bge-large-en-v1.5": "nateraw/bge-large-en-v1.5:9cf9f015a9cb9c61d1a2610659cdac4a4ca222f2d3707a68517b18c198a9add1"
}

cost_mappings = {
    "openai": "OpenAI",
    "anyscale": "Anyscale",
    "azure": "Azure OpenAI",
    "huggingface": "Huggingface",
    "ai21": "AI21",
    "replicate": "Replicate",
    "cohere": "Cohere",
    "alephalpha": "Aleph Alpha",
    "anthropic": "Anthropic",
    "togetherai": "Together AI",
    "google": "Google",
    "bedrock": "AWS Bedrock",
    "groq": "Groq",
    "Katonic LLM": "Katonic LLM",
    "ollama": "Ollama",
    "openrouter": "OpenRouter",
}