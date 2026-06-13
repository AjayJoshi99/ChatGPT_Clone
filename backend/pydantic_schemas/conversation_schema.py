from pydantic import BaseModel
from datetime import datetime

class CreateConversationRequest(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime