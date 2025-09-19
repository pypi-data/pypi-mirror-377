import os
import requests
from .schemas import PredictSchema
from .models.completion import initialize_model_factory
from .logutils import handle_exception
from typing import Dict, Any, Optional, Union, AsyncGenerator

# logger = Logger("/opt/log_files/completion")

def retrieve_model_metadata(model_id: str, log_ingestor_url: str = "http://log-ingestor.kt-katonic.svc.cluster.local:3000"):
    try:
        FETCH_MODEL_URL = f"{log_ingestor_url}/logs/api/models/get"
        # logger.info(f"FETCH_MODEL_URL: {FETCH_MODEL_URL}")

        payload = {"model_id": model_id}
        response = requests.post(url=FETCH_MODEL_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "model" not in data:
            raise ValueError(
                f"'model data'is missing in response for model_id {model_id}: {data}"
            )
        return data
    except requests.exceptions.RequestException as req_err:
        # logger.error(f"Request error while fetching model data: {req_err}")
        raise ConnectionError(f"Error fetching model data: {str(req_err)}")
    except ValueError as val_err:
        # logger.error(f"Value error in fetch_model_data: {val_err}")
        raise ValueError(str(val_err))
    except Exception as e:
        # logger.error(f"Unexpected error in fetch_model_data: {e}")
        raise RuntimeError(f"Unexpected error: {str(e)}")

def create_model_instance(model_id: str, log_ingestor_url: str = "http://log-ingestor.kt-katonic.svc.cluster.local:3000"):
    try:
        model_data = retrieve_model_metadata(model_id, log_ingestor_url)

        provider = model_data["model"].get("parent")
        model_name = model_data["model"]["metadata"].get("endpoint")
        if model_name is None:
            model_name = model_data["model"]["modelName"]
            provider = model_data["model"]["value"]
            if provider == "katonicLLM":
                provider = "katonic"
        if not provider or not model_name:
            raise ValueError(f"Missing provider or endpoint for model_id {model_id}")
        # logger.info(f"SERVICE_TYPE :: {provider}: {model_name}")
        return initialize_model_factory(model_id, provider, model_name, None)
    except Exception as e:
        # logger.error(f"Error in fetch_model_object: {e}")
        raise RuntimeError(f"Error creating model object: {str(e)}")

async def stream_completion_response(provider, model_object, query):
    if provider in [
        "alephalpha",
        "huggingface",
        "ai21",
        "replicate",
        "togetherai",
        "bedrock",
        "Anyscale",
    ]:
        # logger.info("Fetching response without stream")
        response = model_object.invoke(query)
        if hasattr(response, "content"):
            response = response.content
        yield response
    else:
        # logger.info("Fetching response with stream")
        try:
            previous_token = ""
            async for token in model_object.astream(query):
                if hasattr(token, "content"):
                    token = token.content
                    if previous_token != " " and token == "<":
                        token = " <"
                    if previous_token == "(" and token == "<":
                        token = " <"
                    if token == "(<":
                        token = "( <"
                    if token == ">[":
                        token = ">"
                    if token == "]<":
                        token = "<"
                    previous_token = token
                    yield token
                else:
                    yield token
        except Exception:
            err_msg = handle_exception()
            # logger.error(f"Caught exception in asynchronous iterator: {err_msg}")
            yield str(err_msg)
        finally:
            pass  # Streaming finished

def generate_completion(
    model_id: str, 
    data: Dict[str, Any], 
    user: Optional[str] = "anonymous",
    # Platform logging parameters
    save_messages_api: str = "",
    server_domain: str = "",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    enable_logging: bool = True,
    offline_environment: bool = False,
    # Model metadata parameters
    log_ingestor_url: str = "http://log-ingestor:3000"
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Generate completion using LLM models.
    
    Args:
        model_id: The ID of the model to use
        data: Dictionary containing the query and other parameters
        user: User identifier (default: "anonymous")
    
    Returns:
        Union[str, AsyncGenerator[str, None]]: Either a string response or async generator for streaming
        
    Raises:
        ValueError: If required parameters are missing
        ConnectionError: If model data cannot be fetched
        RuntimeError: If model object creation fails
    """
    try:
        # logger.info(f"Payload for llm api access: model_id={model_id}, data={data}, user={user}")
        
        model_data = retrieve_model_metadata(model_id, log_ingestor_url)
        model_name = model_data["model"]["metadata"].get("endpoint")
        provider = model_data["model"].get("parent")
        # logger.info(f"MODEL_ID: {model_id}")

        if "query" not in data:
            raise ValueError("'query' key is missing in the request payload")
        
        # Handle vision models
        if "image_url" in data and provider == "OpenAI":
            from .multimodal.openai_vision import process_vision_request
            result = process_vision_request(
                data["image_url"],
                data["query"],
                model_id,
                model_name,
                None  # logger parameter removed
            )
            return result
            
        model_object = create_model_instance(model_id, log_ingestor_url)
        
        if data.get("stream") == True:
            return stream_completion_response(provider, model_object, data["query"])
            
        result = model_object.invoke(data["query"])
        if hasattr(result, "content"):
            return result.content
        else:
            raise ValueError("Model response does not contain 'content'")
            
    except ValueError as ve:
        # logger.error(f"Validation error: {ve}")
        raise ValueError(str(ve))
    except Exception as e:
        # logger.error(f"Internal error: {e}")
        raise RuntimeError(f"Internal server error: {str(e)}")


def generate_completion_with_schema(
    elements: PredictSchema,
    save_messages_api: str = "",
    server_domain: str = "",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    enable_logging: bool = True,
    offline_environment: bool = False,
    log_ingestor_url: str = "http://log-ingestor.kt-katonic.svc.cluster.local:3000"
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Generate completion using LLM models with PredictSchema.
    
    Args:
        elements: PredictSchema object containing model_id, data, and user
        save_messages_api: Platform API endpoint for logging
        server_domain: Server domain for API calls
        token_name: Token identifier for logging
        project_name: Project identifier for logging
        project_type: Type of project for logging
        product_type: Product type for logging
        enable_logging: Enable/disable platform logging
        offline_environment: Skip token counting in offline mode
        log_ingestor_url: URL for the log ingestor service
        
    Returns:
        Union[str, AsyncGenerator[str, None]]: Either a string response or async generator for streaming
    """
    return generate_completion(
        elements.model_id, 
        elements.data, 
        elements.user,
        save_messages_api=save_messages_api,
        server_domain=server_domain,
        token_name=token_name,
        project_name=project_name,
        project_type=project_type,
        product_type=product_type,
        enable_logging=enable_logging,
        offline_environment=offline_environment,
        log_ingestor_url=log_ingestor_url
    )
