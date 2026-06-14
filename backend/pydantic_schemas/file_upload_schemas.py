from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    document_id: int
    status: str