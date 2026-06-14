from fastapi import (
    APIRouter,
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    HTTPException,
)

from pathlib import Path
from langchain_groq import ChatGroq
from typing import Annotated
from sqlalchemy.orm import Session

from utils.groq_llm import get_groq_client
from database.connection import get_db
from pydantic_schemas.chat_schema import MessageSchema, ChatResponse, SendMessageRequest
from pydantic_schemas.conversation_schema import CreateConversationRequest
from pydantic_schemas.file_upload_schemas import UploadDocumentResponse
from core.dependencies import get_current_user

from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from repositories.summary_repository import SummaryRepository
from repositories.long_term_memory_repo import LongTermMemoryRepository
from repositories.document_repository import DocumentRepository

from services.conversation_service import ConversationService
from services.groq_services import LLMService
from services.summary_service import SummaryService
from services.context_builder import ContextBuilder
from services.chat_services import ChatService
from services.long_term_memory_service import LongTermMemoryService
from services.embedding_services import EmbeddingService
from services.vector_store_service import VectorStoreService
from services.document_service import DocumentService

router = APIRouter(
    prefix="/conversations",
    tags=["chat-with-llm"],
)

CurrentUser = Annotated[dict, Depends(get_current_user)]


def get_conversation_service(
    db: Annotated[Session, Depends(get_db)],
) -> ConversationService:
    """Provides a configured ConversationService instance."""
    return ConversationService(db)


def get_chat_service(db: Annotated[Session, Depends(get_db)]) -> ChatService:
    """Assembles and provides a configured ChatService instance with its full tree of dependencies."""
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    summary_repo = SummaryRepository(db)
    memory_repo = LongTermMemoryRepository(db)
    document_repo = DocumentRepository(db)
    llm_service = LLMService()

    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()
    document_service = DocumentService(
        document_repo, embedding_service, vector_store_service
    )

    long_term_service = LongTermMemoryService(
        memory_repo, llm_service, embedding_service, vector_store_service
    )

    summary_service = SummaryService(
        summary_repository=summary_repo,
        message_repository=message_repo,
        llm_service=llm_service,
    )

    context_builder = ContextBuilder(
        summary_repository=summary_repo,
        message_repository=message_repo,
        long_term_memory_service=long_term_service,
        document_service=document_service,
    )

    return ChatService(
        conversation_repository=conversation_repo,
        message_repository=message_repo,
        groq_service=llm_service,
        summary_service=summary_service,
        context_builder=context_builder,
        long_term_memory=long_term_service,
    )


def get_document_service(db: Annotated[Session, Depends(get_db)]) -> DocumentService:

    document_repo = DocumentRepository(db)

    embedding_service = EmbeddingService()

    vector_store_service = VectorStoreService()

    return DocumentService(
        document_repository=document_repo,
        embedding_service=embedding_service,
        vector_store_service=vector_store_service,
    )


@router.get("/ping-llm")
async def ping_llm(
    message: MessageSchema, llm_client: Annotated[ChatGroq, Depends(get_groq_client)]
):
    response = llm_client.invoke(message)
    return response.content


@router.post("")
async def create_conversation(
    user: CurrentUser,
    request: CreateConversationRequest,
    conv_service: Annotated[ConversationService, Depends(get_conversation_service)],
):
    return await conv_service.create_conversation(user_id=user["user_id"], title=request.title)


@router.get("/")
async def list_conversations(
    user: CurrentUser,
    conv_service: Annotated[ConversationService, Depends(get_conversation_service)],
):
    return await conv_service.get_user_conversations(user_id=user["user_id"])


@router.delete("/{conversation_id}")
async def delete_conversation(
    user: CurrentUser,
    conversation_id: int,
    conv_service: Annotated[ConversationService, Depends(get_conversation_service)],
):
    return await conv_service.delete_conversation(
        conversation_id=conversation_id, user_id=user["user_id"]
    )


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    user: CurrentUser,
    conversation_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_messages(conversation_id=conversation_id, user_id=user["user_id"])


@router.post("/{conversation_id}/messages")
async def send_message(
    user: CurrentUser,
    conversation_id: int,
    request: SendMessageRequest,
    background_task: BackgroundTasks,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    result =  await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=user["user_id"],
        message=request.message,
        background_tasks=background_task,
    )

    return result


@router.post(
    "/{conversation_id}/documents",
    response_model=UploadDocumentResponse,
)
async def upload_document(
    user: CurrentUser,
    conversation_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    document_service: Annotated[
        DocumentService,
        Depends(get_document_service),
    ] = None,
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    upload_root = Path("uploads")

    upload_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file_path = upload_root / f"temp_{file.filename}"

    file_content = await file.read()

    with open(temp_file_path, "wb") as f:
        f.write(file_content)

    try:
        document = await document_service.upload_document(
            conversation_id=conversation_id,
            user_id=user["user_id"],
            file_name=file.filename,
            file_path=str(temp_file_path),
        )

        document_dir = upload_root / str(document.id)

        document_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        final_file_path = document_dir / file.filename

        temp_file_path.rename(final_file_path)

        await document_service.document_repository.update_file_path(
            document_id=document.id,
            file_path=str(final_file_path),
        )

        background_tasks.add_task(
            document_service.process_document,
            document.id,
        )

        return UploadDocumentResponse(
            document_id=document.id,
            status=document.status,
        )

    except Exception as e:

        if temp_file_path.exists():
            temp_file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}",
        )

