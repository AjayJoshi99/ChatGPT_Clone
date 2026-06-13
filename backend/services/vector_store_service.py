import chromadb


class VectorStoreService:

    def __init__(self):

        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.client.get_or_create_collection(name="user_memories")

    async def add_memory(
        self,
        memory_id: int,
        user_id: int,
        memory_text: str,
        embedding: list[float],
    ):

        self.collection.add(
            ids=[str(memory_id)],
            documents=[memory_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "user_id": user_id,
                }
            ],
        )

    async def search_memories(
        self,
        user_id: int,
        query_embedding: list[float],
        limit: int = 5,
    ):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where={"user_id": user_id},
        )

        return results

    async def delete_memory(
        self,
        memory_id: int,
    ):

        self.collection.delete(ids=[str(memory_id)])
