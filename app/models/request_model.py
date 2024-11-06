from pydantic import BaseModel

class DocumentUrlRequest(BaseModel):
    url: str

