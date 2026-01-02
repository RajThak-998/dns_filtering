from pydantic import BaseModel

class PolicyUpdate(BaseModel):
    client_group: str
    category: str
    allowed: bool