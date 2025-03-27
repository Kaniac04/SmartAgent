from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):

    MONGODB_URL: str = os.getenv("MONGODB_URL")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME: str = "web_scraped_data"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

settings = Settings()