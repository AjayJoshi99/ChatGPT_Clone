class LongTermMemoryService:

    def __init__(
        self,
        memory_repository,
        llm_service,
        embedding_service,
        vector_store_service,
    ):
        self.memory_repository = memory_repository
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service

    async def extract_and_store(
        self,
        user_id: int,
        conversation_id: int,
        message: str,
    ):

        print(f"Function is called with parameters {user_id}, {conversation_id} {message}")
        memories = await self.llm_service.extract_memories_from(
            message=message,
        )

        print("Memories retrived ", memories)
        if not memories:
            return

        for memory_text in memories:

            is_duplicate = await self.is_duplicate_memory(
                user_id=user_id,
                memory_text=memory_text,
            )

            if is_duplicate:
                print("mmemory is duplicated", memory_text)
                continue

            memory = await self.memory_repository.create(
                user_id=user_id,
                source_conversation_id=conversation_id,
                memory_text=memory_text,
            )

            embedding = self.embedding_service.embed(memory_text)

            await self.vector_store_service.add_memory(
                memory_id=memory.id,
                user_id=user_id,
                memory_text=memory_text,
                embedding=embedding,
            )

    async def is_duplicate_memory(
        self,
        user_id: int,
        memory_text: str,
        similarity_threshold: float = 0.90,
    ):

        embedding = self.embedding_service.embed(memory_text)

        results = await self.vector_store_service.search_memories(
            user_id=user_id,
            query_embedding=embedding,
            limit=1,
        )

        distances = results.get("distances", [[]])[0]

        if not distances:
            return False

        similarity = 1 - distances[0]

        return similarity >= similarity_threshold

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

        return results.get(
            "documents",
            [[]],
        )[0]

    async def get_memories(
        self,
        user_id: int,
    ):
        return await self.memory_repository.get_user_memories(
            user_id=user_id,
            limit=20,
        )
