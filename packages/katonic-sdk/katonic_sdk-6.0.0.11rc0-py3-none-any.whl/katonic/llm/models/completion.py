#!/usr/bin/env python
# Script            : Main script to categorize all the foundational models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

from .openai_chat_llm import create_openai_model
from .azure_llm import create_azure_model
from .ai21_llm import create_ai21_model
from .bedrock_llm import create_bedrock_model
from .google_llm import create_google_model
from .openrouter_llm import create_openrouter_model
from .cohere_llm import create_cohere_model
from .lighton_llm import create_lighton_model
from .anyscale_llm import create_anyscale_model
from .replicate_llm import create_replicate_model
from .anthropic_llm import create_anthropic_model
from .alephalpha_llm import create_alephalpha_model
from .togetherai_llm import create_togetherai_model
from .groq_llm import create_groq_model
from .huggingface_llm import create_huggingface_model
from .katonic_llm import create_katonic_model
from .sambanova_llm import create_sambanova_model
from .nvidia_llm import create_nvidia_model
from .perplexity_llm import create_perplexity_model
from .vllm_llm import create_vllm_model
from .tgi_llm import create_tgi_model


def initialize_model_factory(service_type, provider, model_name, logger, module=None):
    if provider == "OpenAI":
        return create_openai_model(service_type, model_name, logger)
    if provider == "OpenRouter":
        return create_openrouter_model(service_type, model_name, logger)
    if provider == "Anyscale":
        return create_anyscale_model(service_type, model_name, logger)
    if provider == "Azure OpenAI":
        return create_azure_model(service_type, logger)
    if provider == "Groq":
        return create_groq_model(service_type, model_name, logger)
    if provider == "Huggingface":
        return create_huggingface_model(service_type, model_name, logger)
    if provider == "AI21":
        return create_ai21_model(service_type, model_name, logger)
    if provider == "Replicate":
        return create_replicate_model(service_type, model_name, logger)
    if provider == "Cohere":
        return create_cohere_model(service_type, model_name, logger)
    if provider == "Aleph Alpha":
        return create_alephalpha_model(service_type, model_name, logger)
    if provider == "Anthropic":
        return create_anthropic_model(service_type, model_name, logger)
    if provider == "Together AI":
        return create_togetherai_model(service_type, model_name, logger)
    if provider == "AWS Bedrock":
        return create_bedrock_model(service_type, model_name, logger)
    if provider == "lighton":
        return create_lighton_model(service_type, model_name, logger)
    if provider == "Google":
        return create_google_model(service_type, model_name, logger)
    # if provider == "ollama":
    #     return ollama_completion(service_type, model_name, logger)
    if provider == "Katonic LLM":
        return create_katonic_model(service_type, logger, model_name)
    if provider == "Sambanova":
        return create_sambanova_model(service_type, model_name, logger)
    if provider == "Nvidia":
        return create_nvidia_model(service_type, model_name, logger)
    if provider == "Perplexity":
        return create_perplexity_model(service_type, model_name, logger)
    if provider == "VLLM LLM":
        return create_vllm_model(service_type,logger)
    if provider == "TGI LLM":
        return create_tgi_model(service_type, logger)
    if provider == "katonic":
        return create_katonic_model(service_type, logger, model_name, module)