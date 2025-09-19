from pydantic import BaseModel
from typing import Optional, Any, Dict

class PredictSchema(BaseModel):
    data: Dict[str, Any]
    user: Optional[str] = "anonymous"
    model_id: str
