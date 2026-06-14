from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_schemas.db_tables import Document


class DocumentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        conversation_id: int,
        user_id: int,
        file_name: str,
        file_path: str,
    ) -> Document:

        document = Document(
            conversation_id=conversation_id,
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            status="processing",
        )

        self.db.add(document)

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_by_id(
        self,
        document_id: int,
    ) -> Document | None:

        query = select(Document).where(Document.id == document_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_conversation_documents(
        self,
        conversation_id: int,
    ) -> list[Document]:

        query = (
            select(Document)
            .where(Document.conversation_id == conversation_id)
            .order_by(Document.id.desc())
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: int,
        status: str,
    ):

        document = await self.get_by_id(document_id)

        if not document:
            return None

        document.status = status

        await self.db.commit()

        return document

    async def update_file_path(
        self,
        document_id: int,
        file_path: str,
    ):

        document = await self.get_by_id(
            document_id
        )

        if not document:
            return None

        document.file_path = file_path

        await self.db.commit()

        return document