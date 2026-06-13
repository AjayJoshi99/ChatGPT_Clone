from sqlalchemy import select

from db_schemas.db_tables import ConversationSummary


class SummaryRepository:

    def __init__(self, db):
        self.db = db

    async def get_by_conversation_id(self, conversation_id: int):

        result = await self.db.execute(
            select(ConversationSummary).where(
                ConversationSummary.conversation_id == conversation_id
            )
        )

        return result.scalar_one_or_none()

    async def create(self, conversation_id: int, summary: str):

        summary_obj = ConversationSummary(
            conversation_id=conversation_id, summary=summary
        )

        self.db.add(summary_obj)

        await self.db.commit()
        await self.db.refresh(summary_obj)

        return summary_obj

    async def update(self, summary_obj, summary: str):

        summary_obj.summary = summary

        await self.db.commit()
        await self.db.refresh(summary_obj)

        return summary_obj
