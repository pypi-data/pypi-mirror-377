
import os
from langchain_groq.chat_models import ChatGroq
from ..utilities.utils import decrypt_encryption_seed
from ..utilities.mongo_init import retrieve_model_metadata_from_mongo

def create_groq_model(service_type, model_name, logger=None):
    try:
        fm_meta = retrieve_model_metadata_from_mongo(service_type)
        groq_llm = ChatGroq(
        model_name=model_name,
        groq_api_key=decrypt_encryption_seed(fm_meta["apiKey"]),
        temperature=float(os.environ["TEMPERATURE"])
        if "TEMPERATURE" in os.environ
        else 0.3,
            # max_tokens=int(os.environ["MAXTOKENS"])
            # if "MAXTOKENS" in os.environ
            # else 256,
        )
        return groq_llm
    except Exception as e:
        return str(e)
