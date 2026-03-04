import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from app.rag.embedding_service import EmbeddingService
from app.repositories.knowledge_repository import KnowledgeRepository
from app.entities.schemas import KnowledgeChunkCreate

logger = logging.getLogger(__name__)

class KnowledgeIngestionPipeline:
    """
    Pipeline for ingesting documents and creating knowledge chunks
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.knowledge_repo = KnowledgeRepository(db)
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 100  # Overlap between chunks
    
    def chunk_text(self, text: str, source: str) -> List[KnowledgeChunkCreate]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the end position
                for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                    if text[i:i+2] in ['. ', '! ', '? ']:
                        end = i + 2
                        break
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunk = KnowledgeChunkCreate(
                    content=chunk_content,
                    source=source,
                    chunk_index=chunk_index,
                    chunk_metadata={
                        "start_pos": start,
                        "end_pos": end,
                        "char_count": len(chunk_content)
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)
            
            if start >= len(text):
                break
        
        return chunks
    
    async def ingest_text(
        self, 
        text: str, 
        source: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Ingest text content and create knowledge chunks"""
        logger.info(f"Starting ingestion for source: {source}")
        
        # Clear existing chunks from this source
        deleted_count = self.knowledge_repo.delete_chunks_by_source(source)
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing chunks from {source}")
        
        # Create text chunks
        text_chunks = self.chunk_text(text, source)
        logger.info(f"Created {len(text_chunks)} text chunks")
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.content for chunk in text_chunks]
        embeddings = await self.embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Store chunks with embeddings
        chunk_ids = []
        for chunk, embedding in zip(text_chunks, embeddings):
            # Add metadata to chunk
            if metadata:
                chunk.chunk_metadata.update(metadata)
            
            db_chunk = self.knowledge_repo.create_chunk(chunk, embedding)
            chunk_ids.append(str(db_chunk.id))
        
        logger.info(f"Successfully ingested {len(chunk_ids)} chunks for {source}")
        return chunk_ids
    
    async def ingest_file(self, file_path: str) -> List[str]:
        """Ingest a text file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        metadata = {
            "file_name": path.name,
            "file_size": path.stat().st_size,
            "file_extension": path.suffix,
            "ingestion_type": "file"
        }
        
        return await self.ingest_text(content, str(path), metadata)
    
    async def ingest_directory(
        self, 
        directory_path: str, 
        file_extensions: List[str] = [".txt", ".md", ".py"]
    ) -> Dict[str, List[str]]:
        """Ingest all files in a directory"""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = {}
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    chunk_ids = await self.ingest_file(str(file_path))
                    results[str(file_path)] = chunk_ids
                    logger.info(f"Ingested {file_path}: {len(chunk_ids)} chunks")
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    results[str(file_path)] = []
        
        return results
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get statistics about ingested knowledge"""
        total_chunks = self.knowledge_repo.get_chunk_count()
        sources = self.knowledge_repo.get_sources_list()
        
        stats = {
            "total_chunks": total_chunks,
            "total_sources": len(sources),
            "sources": sources
        }
        
        return stats
