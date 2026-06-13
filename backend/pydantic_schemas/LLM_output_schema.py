from pydantic import BaseModel


class MemoryExtraction(BaseModel):
    memories: list[str]