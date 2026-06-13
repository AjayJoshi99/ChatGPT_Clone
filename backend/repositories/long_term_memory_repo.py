from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_schemas.db_tables import Memory


class LongTermMemoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        source_conversation_id: int,
        memory_text: str,
    ):
        memory = Memory(
            user_id=user_id,
            source_conversation_id=source_conversation_id,
            memory_text=memory_text,
        )

        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        return memory

    async def get_user_memories(
        self,
        user_id: int,
        limit: int = 20,
    ):
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def memory_exists(
        self,
        user_id: int,
        memory_text: str,
    ):
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.memory_text == memory_text,
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none() is not None
