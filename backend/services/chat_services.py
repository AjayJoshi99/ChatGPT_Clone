from fastapi import HTTPException, BackgroundTasks


class ChatService:

    def __init__(
        self,
        conversation_repository,
        message_repository,
        groq_service,
        summary_service,
        context_builder,
        long_term_memory,
    ):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.llm_service = groq_service
        self.summary_service = summary_service
        self.context_builder = context_builder
        self.long_term_memory = long_term_memory

    async def get_messages(self, conversation_id: int, user_id: int):

        conversation = await self.conversation_repository.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(detail="Conversation not found", status_code=402)

        if conversation.user_id != user_id:
            raise HTTPException(detail="Access denied", status_code=401)

        return await self.message_repository.get_by_conversation(conversation_id)

    async def send_message(
        self,
        conversation_id: int,
        user_id: int,
        message: str,
        background_tasks: BackgroundTasks,
    ):
        await self.message_repository.create(
            conversation_id=conversation_id, role="user", content=message
        )

        history = await self.context_builder.build(
            conversation_id, user_id=user_id, current_message=message
        )

        message_count = await self.message_repository.count_messages(conversation_id)

        response = await self.llm_service.generate_response(history)

        await self.message_repository.create(
            conversation_id=conversation_id, role="assistant", content=response
        )

        background_tasks.add_task(
            self.long_term_memory.extract_and_store,
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
        )

        if message_count > 0 and message_count % 40 == 0:
            await self.summary_service.update_summary(conversation_id)

        print(message_count)
        if message_count == 2:
            title = await self.llm_service.generate_title(user_message=message)

            print(title)
            await self.conversation_repository.update_title(conversation_id, title)

        return {"response": response}
