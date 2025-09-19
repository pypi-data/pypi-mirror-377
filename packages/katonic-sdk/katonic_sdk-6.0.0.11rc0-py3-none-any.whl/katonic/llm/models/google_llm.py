import os
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo


def create_google_model(service_type, model_name, logger):
    fm_meta = retrieve_model_metadata_from_mongo(service_type)
    logger.info("------------------ Started Google Completion ------------------")
    try:
        if "text-bison-001" in model_name:
            return GoogleGenerativeAI(
                model=model_name,
                google_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
                temperature=float(os.environ["TEMPERATURE"])
                if "TEMPERATURE" in os.environ
                else 0.3,
            )
        if "gemini-pro" in model_name:
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
                temperature=float(os.environ["TEMPERATURE"])
                if "TEMPERATURE" in os.environ
                else 0.3,
            )
    except Exception as e:
        logger.info(str(e))
        return str(e)
