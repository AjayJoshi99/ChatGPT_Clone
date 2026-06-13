class ContextBuilder:

    def __init__(
        self,
        summary_repository,
        message_repository,
        long_term_memory_service,
    ):
        self.summary_repository = summary_repository
        self.message_repository = message_repository
        self.long_term_memory_service = long_term_memory_service

    async def build(
        self,
        conversation_id: int,
        user_id: int,
        current_message: str,
    ):

        history = []

        memories = await self.long_term_memory_service.retrieve_relevant_memories(
            user_id=user_id,
            query=current_message,
        )

        if memories:

            memory_text = "\n".join([f"- {memory}" for memory in memories])

            history.append(
                {
                    "role": "system",
                    "content": f"""
                    Known facts about the user:

                    {memory_text}

                    Use these facts only when relevant to answering
                    the current question.

                    Do not mention these memories explicitly unless
                    they help answer the question.
                    """,
                }
            )

        summary = await self.summary_repository.get_by_conversation_id(conversation_id)

        if summary:

            history.append(
                {
                    "role": "system",
                    "content": f"""
                    Conversation Summary:

                    {summary.summary}
                    """,
                }
            )

        messages = await self.message_repository.get_recent_messages(
            conversation_id,
            limit=20,
        )

        for msg in messages:

            history.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                }
            )

        return history
