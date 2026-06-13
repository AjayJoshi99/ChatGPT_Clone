from fastapi import APIRouter, Depends
from langchain_groq import ChatGroq
from typing import Annotated
from sqlalchemy.orm import Session

from utils.groq_llm import get_groq_client
from database.connection import get_db
from pydantic_schemas.chat_schema import MessageSchema



router = APIRouter(
    prefix="/conversations",
    tags=["chat-with-llm"],
)


@router.get("/ping-llm")
async def ping_llm(message : MessageSchema, llm_client : Annotated[ChatGroq, Depends(get_groq_client)]):
    response = llm_client.invoke(message)
    return response.content


@router.post("/")
async def create_conversation(messages : MessageSchema, llm_client : Annotated[ChatGroq, Depends(get_groq_client)], db: Annotated[Session, Depends(get_db)]):
    response = llm_client.invoke(messages)
    # create title for the conversation based on the first message
    return response.content


@router.get("/")
async def list_conversations(db: Annotated[Session, Depends(get_db)]):
    return {"message": "This endpoint is for listing all conversations."}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int, db: Annotated[Session, Depends(get_db)]):
    return {"message": "This endpoint is for deleting a specific conversation."}


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, db: Annotated[Session, Depends(get_db)]):
    return {"message": "This endpoint is for retrieving messages within a specific conversation."}

    
@router.post("/{conversation_id}/messages")
async def chat(conversation_id: int, message: MessageSchema, db: Annotated[Session, Depends(get_db)]):
    return {"message": "This endpoint is for adding a new message to a specific conversation."}

