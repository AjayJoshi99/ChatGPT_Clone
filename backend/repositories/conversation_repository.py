from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db_schemas.db_tables import Conversation
from db_schemas.db_tables import Message


class ConversationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, title: str) -> Conversation:

        conversation = Conversation(user_id=user_id, title=title)

        self.db.add(conversation)

        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_by_user_id(self, user_id: int):
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return result.scalars().all()

    async def get_by_conversation(self, conversation_id: int):
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )

        return result.scalars().all()

    async def update_title(self, conversation_id: int, title: str):

        conversation = await self.get_by_id(conversation_id)

        conversation.title = title

        await self.db.commit()

        return conversation

    async def get_by_id(self, conversation_id: int):

        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )

        return result.scalar_one_or_none()

    async def delete(self, conversation):
        await self.db.delete(conversation)
        await self.db.commit()
