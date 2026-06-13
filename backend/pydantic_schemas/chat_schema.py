from pydantic import BaseModel

class MessageSchema(BaseModel):
    content: str