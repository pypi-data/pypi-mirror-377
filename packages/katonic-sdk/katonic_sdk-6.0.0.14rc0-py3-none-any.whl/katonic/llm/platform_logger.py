#!/usr/bin/env python
#
# Copyright (c) 2024 Katonic Pty Ltd. All rights reserved.
#

import asyncio
import hashlib
import json
import os
import re
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    import warnings
    warnings.warn(
        "tiktoken not available. Token counting will be disabled. "
        "Install with 'pip install katonic[llm_deps]' to enable token counting.",
        UserWarning
    )

# Logger removed

def _get_model_provider(model_name: str) -> str:
    """Get model provider based on model name - simplified version"""
    model_name_lower = model_name.lower()
    
    if "cohere" in model_name_lower:
        return "Cohere"
    elif "anthropic" in model_name_lower or "claude" in model_name_lower:
        return "Anthropic"
    elif "openai" in model_name_lower or "gpt" in model_name_lower:
        return "OpenAI"
    elif "llama" in model_name_lower:
        return "Llama"
    else:
        return "Unknown"

def _get_encoding_for_model(model_name: str, offline_environment: bool = False):
    """Get appropriate encoding for the model - based on callback.py logic"""
    try:
        if offline_environment or not TIKTOKEN_AVAILABLE:
            return None
            
        provider = _get_model_provider(model_name)
        
        if provider == "Cohere":
            # For Cohere models, use cl100k_base as fallback
            return tiktoken.get_encoding("cl100k_base")
        elif "llama-2" in model_name.lower():
            # For Llama-2 models
            return tiktoken.get_encoding("cl100k_base")
        elif "llama-3" in model_name.lower():
            # For Llama-3 models
            return tiktoken.get_encoding("cl100k_base")
        elif provider == "Anthropic":
            # For Anthropic models
            return tiktoken.get_encoding("cl100k_base")
        elif "4o" in model_name.lower():
            # For GPT-4o models
            return tiktoken.get_encoding("o200k_base")
        else:
            # Default to cl100k_base
            return tiktoken.get_encoding("cl100k_base")
            
    except Exception as e:
        return None

def _calculate_tokens_and_cost(input_text: str, output_text: str, model_name: str, model_pricing: Optional[Dict] = None, offline_environment: bool = False):
    """Calculate tokens and costs based on model pricing - based on callback.py logic"""
    encoding = _get_encoding_for_model(model_name, offline_environment)
    
    input_token_length = 0
    output_token_length = 0
    input_cost = 0.0
    output_cost = 0.0
    
    if encoding:
        try:
            # Try with disallowed_special first, fallback to regular encode
            try:
                input_tokens = encoding.encode(input_text, disallowed_special=())
                output_tokens = encoding.encode(output_text, disallowed_special=())
            except Exception:
                input_tokens = encoding.encode(input_text)
                output_tokens = encoding.encode(output_text)
                
            input_token_length = len(input_tokens)
            output_token_length = len(output_tokens)
            
        except Exception as e:
            input_token_length = 0
            output_token_length = 0
    
    # Calculate costs if pricing is available
    if model_pricing and "inputCostPerToken" in model_pricing and "outputCostPerToken" in model_pricing:
        input_cost = input_token_length * float(model_pricing["inputCostPerToken"])
        output_cost = output_token_length * float(model_pricing["outputCostPerToken"])
        
        # Handle special cases like Perplexity Online models
        if "32k-online" in model_name and "costPerRequest" in model_pricing:
            output_cost += float(model_pricing["costPerRequest"])
    else:
        # Default GPT-4o rates if no pricing available
        input_cost_per_token = 0.005 / 1000  # $0.005 per 1K tokens
        output_cost_per_token = 0.015 / 1000  # $0.015 per 1K tokens
        input_cost = input_token_length * input_cost_per_token
        output_cost = output_token_length * output_cost_per_token
    
    return input_token_length, output_token_length, input_cost, output_cost

def _generate_conversation_id(query: str, user_email: str):
    """Generate unique conversation ID"""
    timestamp = hex(int(time.time()))[2:].zfill(8)
    random_part = hashlib.md5(f"{query}{user_email}{time.time()}".encode()).hexdigest()[:16]
    return f"{timestamp}{random_part}"

def _get_citation_tokens(text: str) -> List[int]:
    """Extract citation tokens from text - based on callback.py logic"""
    try:
        doc_references = re.findall(r"<span>(\d+)</span>", text)
        final_doc_references = list(set(int(i) for i in doc_references))
        return final_doc_references
    except Exception as e:
        return []

async def _save_citations(conversation_id: str, citations: List[int], server_domain: str):
    """Save citations to the platform - based on callback.py logic"""
    try:
        target_url = f"{server_domain}/logs/api/citations/add"
        payload = {
            "messageId": conversation_id,
            "citations": citations
        }
        
        response = requests.post(url=target_url, json=payload, verify=False)
        
        if response.status_code == 200:
            pass  # Success case
        else:
            pass  # Error case
            
    except Exception as e:
        pass  # Exception case

async def log_to_katonic_platform(
    query: str,
    response: str,
    model_name: str,
    save_messages_api: str = "",
    server_domain: str = "",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    user_email: str = "anonymous",
    processing_time: float = 0.0,
    context: Optional[str] = None,
    status: str = "Success",
    answered: bool = True,
    feedback: Optional[str] = None,
    conversation_id: Optional[str] = None,
    model_pricing: Optional[Dict] = None,
    embedding_model_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    restricted_items_pattern: Optional[Any] = None,
    restriction_message: Optional[str] = None,
    chatmode: Optional[str] = None,
    offline_environment: bool = False,
    enable_logging: bool = True
) -> None:
    """
    Log request to Katonic platform - based on callback.py implementation
    
    Args:
        query: User input query
        response: Model response
        model_name: Name of the model used
        save_messages_api: Platform API endpoint
        server_domain: Server domain for API calls
        token_name: Token identifier
        project_name: Project identifier
        project_type: Type of project
        product_type: Product type
        user_email: User email/identifier
        processing_time: Time taken to process the request
        context: Additional context information
        status: Request status (Success/Failed)
        answered: Whether the query was answered
        feedback: User feedback if any
        conversation_id: Unique conversation ID (auto-generated if not provided)
        model_pricing: Model pricing information
        embedding_model_name: Embedding model name if used
        start_time: Start time of the request
        end_time: End time of the request
        restricted_items_pattern: Pattern for restricted content
        restriction_message: Message for restricted content
        chatmode: Chat mode (e.g., "search knowledge", "ace copilot")
        offline_environment: Skip token counting in offline mode
        enable_logging: Enable/disable logging
    """
    if not enable_logging:
        return
        
    try:
        
        # Validate inputs
        if not query or not isinstance(query, str):
            return
            
        if not isinstance(response, str):
            return
        
        # Define variables upfront - matching callback.py structure
        input_text = query
        output_text = response
        
        
        # Calculate tokens and costs
        input_token_length, output_token_length, input_cost, output_cost = _calculate_tokens_and_cost(
            input_text, output_text, model_name, model_pricing, offline_environment
        )
        
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = _generate_conversation_id(query, user_email)
        
        
        # Handle restricted content - based on callback.py logic
        prediction = output_text
        if restricted_items_pattern is not None:
            matches = restricted_items_pattern.search(output_text)
            if matches:
                prediction = restriction_message or "Content restricted"
        
        # Calculate latency - based on callback.py logic
        if start_time and end_time:
            latency = round((end_time - start_time).total_seconds(), 4)
        else:
            latency = round(processing_time, 4)
        
        # Create payload - matching callback.py structure exactly
        payload = {
            "userName": user_email or "anonymous",
            "projectName": project_name,
            "projectType": project_type,
            "productType": product_type,
            "modelName": model_name if model_name is not None else project_name,
            "embeddingModelName": embedding_model_name,
            "inputTokenCost": round(input_cost, 4),
            "inputTokens": input_token_length,
            "outputTokenCost": round(output_cost, 4),
            "outputTokens": output_token_length,
            "totalCost": round(input_cost + output_cost, 4),
            "totalTokens": input_token_length + output_token_length,
            "request": input_text,
            "response": output_text,
            "context": context or input_text,
            "latency": latency,
            "feedback": feedback,
            "status": status,
            "answered": answered,
            "conversationId": conversation_id,
            "tokenName": token_name,
        }
        
        
        # Determine API endpoint - based on callback.py logic
        if server_domain:
            target_url = f"{server_domain}/logs/api/message/add"
        else:
            target_url = save_messages_api
        
        if not target_url:
            return
            
        
        # API call to Katonic - based on callback.py logic
        try:
            response = requests.post(
                url=target_url,
                json=payload,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200 and response.json().get("status") == 200:
                pass  # Success case - no action needed
            else:
                pass  # Error case - no action needed
                
        except Exception as e:
            pass  # Exception case - no action needed
        
        # Handle citations if available - based on callback.py logic
        citations = _get_citation_tokens(output_text)
        if citations and server_domain:
            await _save_citations(conversation_id, citations, server_domain)
            
    except Exception as e:
        pass  # Exception case - no action needed

def log_to_katonic_platform_sync(
    query: str,
    response: str,
    model_name: str,
    save_messages_api: str = "",
    server_domain: str = "",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    user_email: str = "anonymous",
    processing_time: float = 0.0,
    context: Optional[str] = None,
    status: str = "Success",
    answered: bool = True,
    feedback: Optional[str] = None,
    conversation_id: Optional[str] = None,
    model_pricing: Optional[Dict] = None,
    embedding_model_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    restricted_items_pattern: Optional[Any] = None,
    restriction_message: Optional[str] = None,
    chatmode: Optional[str] = None,
    offline_environment: bool = False,
    enable_logging: bool = True
) -> None:
    """
    Synchronous version of log_to_katonic_platform for non-async contexts
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a task
            asyncio.create_task(log_to_katonic_platform(
                query, response, model_name, save_messages_api, server_domain,
                token_name, project_name, project_type, product_type, user_email,
                processing_time, context, status, answered, feedback, conversation_id,
                model_pricing, embedding_model_name, start_time, end_time,
                restricted_items_pattern, restriction_message, chatmode,
                offline_environment, enable_logging
            ))
        else:
            # If no loop is running, run it directly
            loop.run_until_complete(log_to_katonic_platform(
                query, response, model_name, save_messages_api, server_domain,
                token_name, project_name, project_type, product_type, user_email,
                processing_time, context, status, answered, feedback, conversation_id,
                model_pricing, embedding_model_name, start_time, end_time,
                restricted_items_pattern, restriction_message, chatmode,
                offline_environment, enable_logging
            ))
    except RuntimeError:
        # If no event loop exists, create a new one
        asyncio.run(log_to_katonic_platform(
            query, response, model_name, save_messages_api, server_domain,
            token_name, project_name, project_type, product_type, user_email,
            processing_time, context, status, answered, feedback, conversation_id,
            model_pricing, embedding_model_name, start_time, end_time,
            restricted_items_pattern, restriction_message, chatmode,
            offline_environment, enable_logging
        ))