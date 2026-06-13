class SummaryService:

    def __init__(self, summary_repository, message_repository, llm_service):
        self.summary_repository = summary_repository
        self.message_repository = message_repository
        self.llm_service = llm_service

    async def update_summary(self, conversation_id: int):

        summary_obj = await self.summary_repository.get_by_conversation_id(
            conversation_id
        )

        messages = await self.message_repository.get_recent_messages(
            conversation_id, limit=20
        )

        conversation_text = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in messages]
        )

        if summary_obj:

            prompt = f"""
                Current Summary:

                {summary_obj.summary}

                Update the summary using these new messages:

                {conversation_text}

                Return only the updated summary.
                """

        else:

            prompt = f"""
                Create a summary of this conversation:

                {conversation_text}

                Return only the summary.
                """

        new_summary = await self.llm_service.generate_text(prompt)

        if summary_obj:

            await self.summary_repository.update(summary_obj, new_summary)

        else:

            await self.summary_repository.create(conversation_id, new_summary)
