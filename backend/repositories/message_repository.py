from sqlalchemy import select, func

from db_schemas.db_tables import Message


class MessageRepository:

    def __init__(self, db):
        self.db = db

    async def create(self, conversation_id: int, role: str, content: str):

        message = Message(conversation_id=conversation_id, role=role, content=content)

        self.db.add(message)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_recent_messages(self, conversation_id: int, limit: int = 20):

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = result.scalars().all()

        return list(reversed(messages))

    async def count_messages(self, conversation_id: int):

        result = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation_id
            )
        )

        return result.scalar_one()

    async def get_by_conversation(self, conversation_id: int):

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        return result.scalars().all()
