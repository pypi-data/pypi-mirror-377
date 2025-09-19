import os
import requests

def retrieve_model_metadata_from_mongo(model_id):
    LOG_INGESTOR_URL = "http://log-ingestor:3000"
    FETCH_MODEL_URL = LOG_INGESTOR_URL + "/logs/api/models/get"
    payload = {"model_id": model_id}
    return requests.post(url=FETCH_MODEL_URL, json=payload).json()["model"]
