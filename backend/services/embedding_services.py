from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:

    def __init__(self):

        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    def embed(self, text: str):

        return self.embeddings.embed_query(text)
