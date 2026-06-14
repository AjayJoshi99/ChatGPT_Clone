from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str
    HF_TOKEN:str
    SECRET_KEY_ACCESS_TOKEN : str 
    SECRET_KEY_REFRESH_TOKEN : str 
    HASHING_ALGO : str
    TOKEN_ENCODE_ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    REFRESH_TOKEN_EXPIRE_MINUTES : int

settings = Settings()