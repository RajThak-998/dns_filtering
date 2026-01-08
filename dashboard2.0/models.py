from pydantic import BaseModel

class Groups(BaseModel):
    name: str

class Categories(BaseModel):
    name: str

class Clients(BaseModel):
    ip : str
    client_group: str

class Domains(BaseModel):
    domain: str
    category: str

class Policies(BaseModel):
    client_group: str
    category: str
    allowed: int