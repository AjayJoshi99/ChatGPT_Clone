from pydantic import BaseModel

class MessageSchema(BaseModel):
    content: str


class SendMessageRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str