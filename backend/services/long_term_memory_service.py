class LongTermMemoryService:

    def __init__(
        self,
        memory_repository,
        summary_repository,
        message_repository,
        llm_service,
        embedding_service,
        vector_store_service
    ):
        self.memory_repository = memory_repository
        self.summary_repository = summary_repository
        self.message_repository = message_repository
        self.llm_service = llm_service
        self.vector_store_service = vector_store_service
        self.embedding_service = embedding_service

    async def extract_and_store(
        self,
        user_id: int,
        conversation_id: int,
    ):
        summary_obj = await self.summary_repository.get_by_conversation_id(
            conversation_id
        )

        summary = ""

        if summary_obj:
            summary = summary_obj.summary

        messages = await self.message_repository.get_recent_messages(
            conversation_id,
            limit=20,
        )

        recent_text = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])

        memories = await self.llm_service.extract_memories(
            summary=summary,
            recent_messages=recent_text,
        )

        for memory in memories:

            exists = await self.memory_repository.memory_exists(
                user_id=user_id,
                memory_text=memory,
            )

            if exists:
                continue

            memory = await self.memory_repository.create(
                user_id=user_id,
                source_conversation_id=conversation_id,
                memory_text=memory,
            )

            embedding = self.embedding_service.embed(memory.memory_text)

            await self.vector_store_service.add_memory(
                memory_id=memory.id,
                user_id=user_id,
                memory_text=memory.memory_text,
                embedding=embedding,
            )

    async def get_memories(
        self,
        user_id: int,
    ):
        return await self.memory_repository.get_user_memories(
            user_id=user_id,
            limit=20,
        )

    async def retrieve_relevant_memories(
        self,
        user_id: int,
        query: str,
    ):

        query_embedding = self.embedding_service.embed(query)

        results = await self.vector_store_service.search_memories(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=5,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        return documents
