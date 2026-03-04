import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.rag.embedding_service import EmbeddingService
from app.repositories.knowledge_repository import KnowledgeRepository
from app.entities.schemas import AIQuestionRequest, AIResponse
import openai
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation service for AI tutoring
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.knowledge_repo = KnowledgeRepository(db)
        self.client = None
        self._initialize_openai_client()
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client for text generation"""
        if settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized for text generation")
        else:
            logger.warning("OpenAI API key not provided. RAG service will use mock responses.")
    
    async def retrieve_relevant_context(
        self, 
        query: str, 
        max_chunks: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge chunks for a query"""
        
        # Generate embedding for the query
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search for similar chunks
        similar_chunks = self.knowledge_repo.search_similar_chunks(
            query_embedding=query_embedding,
            limit=max_chunks,
            similarity_threshold=similarity_threshold
        )
        
        # Format context information
        context_chunks = []
        for chunk, similarity_score in similar_chunks:
            context_chunks.append({
                "content": chunk.content,
                "source": chunk.source,
                "similarity": similarity_score,
                "chunk_index": chunk.chunk_index,
                "metadata": chunk.chunk_metadata
            })
        
        logger.info(f"Retrieved {len(context_chunks)} relevant chunks for query")
        return context_chunks
    
    def build_prompt(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]], 
        user_skill_level: str = "beginner"
    ) -> str:
        """Build RAG prompt with context and question"""
        
        # System message for art tutoring
        system_prompt = f"""
You are an expert art tutor helping a {user_skill_level} level student. Your role is to:
1. Provide clear, encouraging, and educational responses
2. Use the provided context to give accurate information
3. Adapt your language to the student's skill level
4. Suggest practical exercises when appropriate
5. Be supportive and motivating

Always base your answers on the provided context when available, but you can also draw from your general art knowledge.
"""
        
        # Build context section
        context_text = ""
        if context_chunks:
            context_text = "\n\nRelevant Learning Materials:\n"
            for i, chunk in enumerate(context_chunks, 1):
                source = chunk.get('source', 'Unknown')
                content = chunk['content'][:500] + "..." if len(chunk['content']) > 500 else chunk['content']
                context_text += f"\n{i}. From {source}:\n{content}\n"
        
        # Combine everything
        full_prompt = f"""{system_prompt}

{context_text}

Student Question: {question}

Please provide a helpful, educational response appropriate for a {user_skill_level} level art student:"""
        
        return full_prompt
    
    async def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate AI response using OpenAI"""
        
        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Return mock response for development
                return self._generate_mock_response(prompt)
        
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response for development/testing"""
        return """
I'm here to help with your art learning! However, I'm currently running in development mode. 
To get personalized AI tutoring responses, please configure your OpenAI API key.

In the meantime, here are some general art tips:
- Practice drawing basic shapes regularly
- Study light and shadow
- Observe art from masters
- Keep an art journal
- Don't be afraid to make mistakes - they're part of learning!

Is there a specific art technique or concept you'd like to know more about?
"""
    
    async def ask_question(
        self, 
        request: AIQuestionRequest
    ) -> AIResponse:
        """Main method for handling AI questions with RAG"""
        
        logger.info(f"Processing AI question for user {request.user_id}")
        
        # Retrieve relevant context if requested
        context_chunks = []
        sources = []
        
        if request.include_context:
            context_chunks = await self.retrieve_relevant_context(request.question)
            sources = [chunk['source'] for chunk in context_chunks]
        
        # Get user skill level (you might want to fetch this from user service)
        user_skill_level = "beginner"  # Default, could be retrieved from user data
        
        # Build prompt with context
        prompt = self.build_prompt(
            question=request.question,
            context_chunks=context_chunks,
            user_skill_level=user_skill_level
        )
        
        # Generate AI response
        answer = await self.generate_response(prompt)
        
        # Calculate confidence based on context relevance
        confidence = self._calculate_confidence(context_chunks)
        
        return AIResponse(
            answer=answer,
            sources=list(set(sources)),  # Remove duplicates
            confidence=confidence
        )
    
    def _calculate_confidence(self, context_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieved context"""
        if not context_chunks:
            return 0.3  # Low confidence without context
        
        # Average similarity score of retrieved chunks
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in context_chunks) / len(context_chunks)
        
        # Adjust confidence based on number of relevant chunks
        chunk_bonus = min(0.2, len(context_chunks) * 0.05)
        
        confidence = min(0.95, avg_similarity + chunk_bonus)
        return round(confidence, 2)
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        total_chunks = self.knowledge_repo.get_chunk_count()
        sources = self.knowledge_repo.get_sources_list()
        
        return {
            "total_knowledge_chunks": total_chunks,
            "knowledge_sources": len(sources),
            "available_sources": sources[:10]  # Show first 10 sources
        }
