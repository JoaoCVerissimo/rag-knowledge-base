import hashlib
import json
import logging

from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance: "EmbeddingService | None" = None
    _model: SentenceTransformer | None = None

    def __init__(self) -> None:
        if EmbeddingService._model is None:
            logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
            EmbeddingService._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(
                "Embedding model loaded. Dimension: %d",
                EmbeddingService._model.get_sentence_embedding_dimension(),
            )

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Batch embed texts. Returns list of normalized vectors."""
        embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        embedding = self._model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

    @staticmethod
    def cache_key(text: str) -> str:
        return f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
