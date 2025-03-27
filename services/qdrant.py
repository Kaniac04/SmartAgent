import qdrant_client
from sentence_transformers import SentenceTransformer
from config.config import settings

qdrant_client = qdrant_client.QdrantClient(
    settings.QDRANT_HOST, 
    api_key=settings.QDRANT_API_KEY
)

model = SentenceTransformer(settings.EMBEDDING_MODEL)
