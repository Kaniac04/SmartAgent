import qdrant_client
from config.config import settings

qdrant_client = qdrant_client.QdrantClient(
    settings.QDRANT_HOST, 
    api_key=settings.QDRANT_API_KEY
)

model = SentenceTransformer(settings.EMBEDDING_MODEL)
