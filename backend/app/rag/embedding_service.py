import openai
import tiktoken
import numpy as np
from typing import List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings using OpenAI's API
    """
    
    def __init__(self):
        self.client = None
        self.model = settings.embedding_model
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Used by text-embedding-ada-002
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            logger.info(f"OpenAI client initialized with model: {self.model}")
        else:
            logger.warning("OpenAI API key not provided. Embedding service will use mock embeddings.")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def chunk_text_by_tokens(self, text: str, max_tokens: int = 8000) -> List[str]:
        """Split text into chunks that don't exceed token limit"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence + '. ')
            
            if current_tokens + sentence_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
                current_tokens = sentence_tokens
            else:
                current_chunk += sentence + '. '
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if self.client:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            else:
                # Return mock embedding for development
                return self._generate_mock_embedding(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._generate_mock_embedding(text)
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if self.client and len(texts) <= 100:  # OpenAI batch limit
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            else:
                # Process individually or return mock embeddings
                embeddings = []
                for text in texts:
                    embedding = await self.generate_embedding(text)
                    embeddings.append(embedding)
                return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding for development/testing"""
        # Create a simple hash-based mock embedding
        np.random.seed(hash(text) % (2**32))
        return np.random.normal(0, 1, 1536).tolist()  # 1536 is ada-002 dimension
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return dot_product / (norm_vec1 * norm_vec2)
