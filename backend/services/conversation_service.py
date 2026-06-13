from fastapi import HTTPException

from repositories.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, db_session):
        self.db = db_session
        self.repo = ConversationRepository(db_session)

    async def create_conversation(self, user_id: int, title: str | None):
        if not title:
            title = "New Chat"

        return await self.repo.create(user_id=user_id, title=title)

    async def get_user_conversations(self, user_id: int):
        return await self.repo.get_by_user_id(user_id)

    async def delete_conversation(self, conversation_id: int, user_id: int):

        conversation = await self.repo.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(detail="Conversation not found")

        if conversation.user_id != user_id:
            raise HTTPException(detail="Access denied")

        await self.repo.delete(conversation)

        return {"message": "Conversation deleted successfully"}
