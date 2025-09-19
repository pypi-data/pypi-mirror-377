import requests
from .schemas import PredictSchema
from .models.completion import initialize_model_factory
from .logutils import handle_exception
from typing import Dict, Any, Optional, Union, AsyncGenerator


def fetch_model_data(model_id, logger=None):
    """
    Fetch model data from the log ingestor service.
    This function matches the implementation used in the FastAPI router.
    
    Args:
        model_id: The ID of the model to fetch
        logger: Optional logger instance for logging
        
    Returns:
        dict: Model data from the service
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        LOG_INGESTOR_URL = "http://log-ingestor.kt-katonic.svc.cluster.local:3000"

        FETCH_MODEL_URL = f"{LOG_INGESTOR_URL}/logs/api/models/get"
        if logger:
            logger.info(f"FETCH_MODEL_URL: {FETCH_MODEL_URL}")

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
        if logger:
            logger.error(f"Request error while fetching model data: {req_err}")
        raise ConnectionError(f"Error fetching model data: {str(req_err)}")
    except ValueError as val_err:
        if logger:
            logger.error(f"Value error in fetch_model_data: {val_err}")
        raise ValueError(str(val_err))
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error in fetch_model_data: {e}")
        raise RuntimeError(f"Unexpected error: {str(e)}")

def fetch_model_object(model_id, logger=None):
    """
    Fetch model object by creating an instance using model data.
    This function matches the implementation used in the FastAPI router.
    
    Args:
        model_id: The ID of the model to fetch
        logger: Optional logger instance for logging
        
    Returns:
        Model object instance
        
    Raises:
        RuntimeError: If model object creation fails
    """
    try:
        model_data = fetch_model_data(model_id, logger)

        provider = model_data["model"].get("parent")
        model_name = model_data["model"]["metadata"].get("endpoint")
        if model_name is None:
            model_name = model_data["model"]["modelName"]
            provider = model_data["model"]["value"]
            if provider == "katonicLLM":
                provider = "katonic"
        if not provider or not model_name:
            raise ValueError(f"Missing provider or endpoint for model_id {model_id}")
        if logger:
            logger.info(f"SERVICE_TYPE :: {provider}: {model_name}")
        return get_llm(model_id, provider, model_name, logger)
    except Exception as e:
        if logger:
            logger.error(f"Error in fetch_model_object: {e}")
        raise RuntimeError(f"Error creating model object: {str(e)}")

def get_llm(model_id, provider, model_name, logger=None):
    """
    Get LLM model instance using the model factory.
    This function wraps initialize_model_factory with logger support.
    
    Args:
        model_id: The ID of the model
        provider: The provider name (e.g., "OpenAI", "Anthropic", etc.)
        model_name: The name of the model
        logger: Optional logger instance for logging
        
    Returns:
        Model object instance
    """
    return initialize_model_factory(model_id, provider, model_name, logger)

async def fetch_stream_response(provider, model_object, query, logger=None):
    """
    Fetch streaming response from model object.
    This function matches the implementation used in the FastAPI router.
    
    Args:
        provider: The provider name
        model_object: The model object instance
        query: The query string
        logger: Optional logger instance for logging
        
    Yields:
        str: Response tokens or complete response
    """
    if provider in [
        "alephalpha",
        "huggingface",
        "ai21",
        "replicate",
        "togetherai",
        # "katonic",
        "bedrock",
        "Anyscale",
    ]:
        if logger:
            logger.info("Fetching response without stream")
        response = model_object.invoke(query)
        if hasattr(response, "content"):
            response = response.content
        yield response
    else:
        if logger:
            logger.info("Fetching response with stream")
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
            if logger:
                logger.error(f"Caught exception in asynchronous iterator: {err_msg}")
            yield str(err_msg)
        finally:
            if logger:
                logger.info(f"Streaming finished")


def generate_completion(
    model_id: str, 
    data: Dict[str, Any], 
    user: Optional[str] = "anonymous"
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
        model_data = fetch_model_data(model_id)
        model_name = model_data["model"]["metadata"].get("endpoint")
        provider = model_data["model"].get("parent")

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
                None
            )
            return result
            
        model_object = fetch_model_object(model_id)
        
        if data.get("stream") == True:
            return fetch_stream_response(provider, model_object, data["query"])
            
        result = model_object.invoke(data["query"])
        if hasattr(result, "content"):
            return result.content
        else:
            raise ValueError("Model response does not contain 'content'")
            
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        raise RuntimeError(f"Internal server error: {str(e)}")


def generate_completion_with_schema(
    elements: PredictSchema
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Generate completion using LLM models with PredictSchema.
    
    Args:
        elements: PredictSchema object containing model_id, data, and user
        
    Returns:
        Union[str, AsyncGenerator[str, None]]: Either a string response or async generator for streaming
    """
    return generate_completion(
        elements.model_id, 
        elements.data, 
        elements.user
    )
