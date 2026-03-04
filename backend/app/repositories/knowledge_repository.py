from sqlalchemy.orm import Session
from sqlalchemy import text, desc, func
from typing import List, Optional, Tuple
from uuid import UUID
import numpy as np
from app.entities.models import KnowledgeChunk
from app.entities.schemas import KnowledgeChunkCreate


class KnowledgeRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_chunk(self, chunk: KnowledgeChunkCreate, embedding: List[float]) -> KnowledgeChunk:
        """Create a new knowledge chunk with embedding"""
        db_chunk = KnowledgeChunk(
            content=chunk.content,
            source=chunk.source,
            chunk_index=chunk.chunk_index,
            chunk_metadata=chunk.chunk_metadata,
            embedding=embedding
        )
        
        self.db.add(db_chunk)
        self.db.commit()
        self.db.refresh(db_chunk)
        return db_chunk
    
    def get_chunk_by_id(self, chunk_id: UUID) -> Optional[KnowledgeChunk]:
        """Get knowledge chunk by ID"""
        return self.db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    
    def get_chunks_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[KnowledgeChunk]:
        """Get knowledge chunks from a specific source"""
        return self.db.query(KnowledgeChunk).filter(
            KnowledgeChunk.source == source
        ).order_by(KnowledgeChunk.chunk_index).offset(skip).limit(limit).all()
    
    def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[KnowledgeChunk, float]]:
        """Search for similar knowledge chunks using vector similarity"""
        
        # Format query embedding as pgvector string for raw SQL
        query_vector = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Use pgvector cosine similarity operator
        similarity_query = text("""
            SELECT 
                id, content, source, chunk_index, chunk_metadata, created_at,
                1 - (embedding <=> :query_embedding) as similarity
            FROM knowledge_chunks 
            WHERE (1 - (embedding <=> :query_embedding)) > :threshold
            ORDER BY similarity DESC 
            LIMIT :limit
        """)
        
        try:
            result = self.db.execute(
                similarity_query, 
                {
                    'query_embedding': query_vector,
                    'threshold': similarity_threshold,
                    'limit': limit
                }
            ).fetchall()
            
            chunks_with_scores = []
            for row in result:
                # Reconstruct KnowledgeChunk object
                chunk = KnowledgeChunk(
                    id=row.id,
                    content=row.content,
                    source=row.source,
                    chunk_index=row.chunk_index,
                    chunk_metadata=row.chunk_metadata or {},
                    created_at=row.created_at
                )
                chunks_with_scores.append((chunk, row.similarity))
            
            return chunks_with_scores
        
        except Exception as e:
            # Fallback to basic text search if vector search fails
            print(f"Vector search failed: {e}. Falling back to text search.")
            return self._fallback_text_search(query_embedding, limit)
    
    def _fallback_text_search(self, query_embedding: List[float], limit: int) -> List[Tuple[KnowledgeChunk, float]]:
        """Fallback text search when vector search is not available"""
        # Get all chunks for basic similarity
        chunks = self.db.query(KnowledgeChunk).limit(limit * 3).all()  # Get more for filtering
        
        chunks_with_scores = []
        for chunk in chunks:
            # Simple score based on content length (mock similarity)
            score = min(1.0, len(chunk.content) / 1000.0)  # Normalize by content length
            chunks_with_scores.append((chunk, score))
        
        # Sort by score and return top results
        chunks_with_scores.sort(key=lambda x: x[1], reverse=True)
        return chunks_with_scores[:limit]
    
    def get_all_chunks(self, skip: int = 0, limit: int = 100) -> List[KnowledgeChunk]:
        """Get all knowledge chunks with pagination"""
        return self.db.query(KnowledgeChunk).offset(skip).limit(limit).all()
    
    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a knowledge chunk"""
        chunk = self.get_chunk_by_id(chunk_id)
        if chunk:
            self.db.delete(chunk)
            self.db.commit()
            return True
        return False
    
    def delete_chunks_by_source(self, source: str) -> int:
        """Delete all chunks from a specific source"""
        deleted_count = self.db.query(KnowledgeChunk).filter(
            KnowledgeChunk.source == source
        ).delete()
        self.db.commit()
        return deleted_count
    
    def get_chunk_count(self) -> int:
        """Get total number of knowledge chunks"""
        return self.db.query(KnowledgeChunk).count()
    
    def get_sources_list(self) -> List[str]:
        """Get list of all unique sources"""
        sources = self.db.query(KnowledgeChunk.source).distinct().all()
        return [source[0] for source in sources if source[0]]
