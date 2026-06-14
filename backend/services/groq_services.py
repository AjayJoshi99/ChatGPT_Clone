from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.groq_llm import get_groq_client
from pydantic_schemas.LLM_output_schema import MemoryExtraction


class LLMService:
    def __init__(self):
        self.client = get_groq_client()

    async def generate_response(self, messages: list) -> str:

        chat_messages = []

        for message in messages:

            if message["role"] == "user":
                chat_messages.append(HumanMessage(content=message["content"]))

            elif message["role"] == "assistant":
                chat_messages.append(AIMessage(content=message["content"]))

            elif message["role"] == "system":
                chat_messages.append(SystemMessage(content=message["content"]))

        response = await self.client.ainvoke(chat_messages)

        return response.content

    async def generate_title(self, user_message: str) -> str:

        print("Generating title")
        prompt = f"""
                    Generate a short conversation title based on the user's first message.

                    Rules:
                    - Maximum 5 words.
                    - Do not use quotes.
                    - Do not use punctuation.
                    - Return only the title.

                    User message:
                    {user_message}
                    """

        response = await self.client.ainvoke([HumanMessage(content=prompt)])

        return response.content.strip()

    async def generate_text(self, prompt: str):

        response = await self.client.ainvoke(prompt)

        return response.content

    async def extract_memories(
        self,
        summary: str,
        recent_messages: str,
    ) -> list[str]:

        prompt = f"""
                    You are a memory extraction system.

                    Extract long-term user facts.

                    Store only information likely to remain useful in future conversations.

                    Good examples:
                    - User is preparing for GATE.
                    - User prefers Python.
                    - User works as a backend developer.

                    Bad examples:
                    - User asked about FastAPI.
                    - User wants help today.
                    - User is debugging a specific error.

                    Summary:
                    {summary}

                    Recent Messages:
                    {recent_messages}
                    """

        structured_llm = self.llm.with_structured_output(MemoryExtraction)

        result = await structured_llm.ainvoke(prompt)

        return result.memories

    async def extract_memories_from(
        self,
        message: str,
    ):
        prompt = f"""
                Extract long-term user memories.

                Store only:
                - Name
                - Preferences
                - Goals
                - Skills
                - Experience
                - Personal facts useful in future conversations

                Ignore:
                - Greetings
                - Temporary requests
                - Questions
                - Small talk

                Return JSON list.

                Message:
                {message}
                """

        structured_llm = self.client.with_structured_output(MemoryExtraction)

        response = await structured_llm.ainvoke(prompt)

        return response.memories
