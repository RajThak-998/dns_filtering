from pydantic import BaseModel

class PolicyUpdate(BaseModel):
    client_group: str
    category: str
    allowed: bool

class ClientUpdate(BaseModel):
    ip: str
    client_group: str