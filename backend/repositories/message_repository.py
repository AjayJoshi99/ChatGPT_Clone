class MessageRepository:

    async def create_message(self, conversation_id: int, role: str, content: str):
        pass

    async def get_recent_messages(self, conversation_id: int, limit: int = 20):
        pass

    async def count_messages(self, conversation_id: int):
        pass
