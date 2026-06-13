from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

client = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def get_groq_client():
    return client


