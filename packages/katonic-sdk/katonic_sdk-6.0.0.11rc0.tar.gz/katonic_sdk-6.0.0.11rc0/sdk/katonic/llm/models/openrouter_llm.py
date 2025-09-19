import os
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo
from typing import Optional
from langchain_community.chat_models import ChatOpenAI


class ChatOpenRouter(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(
        self,
        model_name: str,
        openai_api_key: Optional[str] = None,
        openai_api_base: str = "https://openrouter.ai/api/v1",
        **kwargs
    ):
        openai_api_key = openai_api_key or os.getenv("OPENROUTER_API_KEY")
        super().__init__(
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            model_name=model_name,
            **kwargs
        )


def create_openrouter_model(service_type, model_name, logger):
    logger.info("------------------ Started Open Router Completion ------------------")
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        open_router_llm = ChatOpenRouter(
            model_name=model_name,
            openai_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
            temperature=(
                float(os.environ["TEMPERATURE"]) if "TEMPERATURE" in os.environ else 0.7
            ),
            streaming=True
        )
        logger.info("LLM Created Successfully...")
        return open_router_llm
    except Exception as e:
        return str(e)
