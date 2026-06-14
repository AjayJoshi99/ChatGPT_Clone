from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


class DocumentService:

    def __init__(
        self,
        document_repository,
        embedding_service,
        vector_store_service,
    ):
        self.document_repository = document_repository
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service

    async def upload_document(
        self,
        conversation_id: int,
        user_id: int,
        file_name: str,
        file_path: str,
    ):

        return await self.document_repository.create(
            conversation_id=conversation_id,
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
        )

    async def process_document(
        self,
        document_id: int,
    ):

        document = await self.document_repository.get_by_id(document_id)

        if not document:
            return

        try:

            text = self._extract_pdf_text(document.file_path)

            chunks = self._chunk_text(text)

            embeddings = self.embedding_service.embed_documents(chunks)

            ids = []

            metadatas = []

            for index, _ in enumerate(chunks):

                ids.append(f"{document.id}_{index}")

                metadatas.append(
                    {
                        "document_id": document.id,
                        "conversation_id": document.conversation_id,
                        "user_id": document.user_id,
                        "chunk_index": index,
                    }
                )

            await self.vector_store_service.add_document_chunks(
                ids=ids,
                chunks=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            await self.document_repository.update_status(
                document.id,
                "completed",
            )

        except Exception:

            await self.document_repository.update_status(
                document.id,
                "failed",
            )

            raise

    def _extract_pdf_text(
        self,
        file_path: str,
    ) -> str:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    def _chunk_text(
        self,
        text: str,
    ) -> list[str]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        return splitter.split_text(text)

    async def retrieve_relevant_chunks(
        self,
        conversation_id: int,
        query: str,
        limit: int = 5,
    ):

        query_embedding = self.embedding_service.embed(query)

        results = await self.vector_store_service.search_document_chunks(
            conversation_id=conversation_id,
            query_embedding=query_embedding,
            limit=limit,
        )

        return results.get(
            "documents",
            [[]],
        )[0]
