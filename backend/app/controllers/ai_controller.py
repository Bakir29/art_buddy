from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from app.database import get_db
from app.entities.schemas import AIQuestionRequest, AIResponse, User
from app.rag.rag_service import RAGService
from app.rag.ingestion import KnowledgeIngestionPipeline
from app.auth.dependencies import get_current_active_user
import tempfile
import os

router = APIRouter()


@router.post("/ask", response_model=AIResponse)
async def ask_ai_tutor(
    request: AIQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ask the AI tutor a question with RAG-enhanced responses
    """
    # Validate that the user asking matches the request
    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only ask questions as yourself"
        )
    
    rag_service = RAGService(db)
    return await rag_service.ask_question(request)


@router.get("/knowledge-stats")
async def get_knowledge_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics about the knowledge base
    """
    rag_service = RAGService(db)
    return await rag_service.get_knowledge_stats()


@router.post("/ingest-text")
async def ingest_text_content(
    content: str = Form(...),
    source: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingest text content into the knowledge base (admin function)
    """
    # In a real app, you'd check for admin permissions here
    
    ingestion_pipeline = KnowledgeIngestionPipeline(db)
    
    try:
        chunk_ids = await ingestion_pipeline.ingest_text(
            text=content,
            source=source,
            metadata={"ingested_by": str(current_user.id), "type": "manual_text"}
        )
        
        return {
            "message": "Text content ingested successfully",
            "chunks_created": len(chunk_ids),
            "source": source
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest content: {str(e)}"
        )


@router.post("/ingest-file")
async def ingest_file_content(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and ingest a text file into the knowledge base (admin function)
    """
    # Check file type
    allowed_extensions = ['.txt', '.md', '.py', '.json']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
        )
    
    # Create temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Ingest the file
        ingestion_pipeline = KnowledgeIngestionPipeline(db)
        chunk_ids = await ingestion_pipeline.ingest_file(tmp_file_path)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "message": "File ingested successfully",
            "filename": file.filename,
            "chunks_created": len(chunk_ids),
            "file_size": len(content)
        }
    
    except Exception as e:
        # Clean up on error
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest file: {str(e)}"
        )


@router.get("/search-knowledge")
async def search_knowledge_base(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search the knowledge base for relevant content
    """
    rag_service = RAGService(db)
    
    try:
        context_chunks = await rag_service.retrieve_relevant_context(
            query=query,
            max_chunks=limit
        )
        
        return {
            "query": query,
            "results_found": len(context_chunks),
            "results": context_chunks
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.delete("/knowledge/source/{source_name}")
async def delete_knowledge_source(
    source_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete all knowledge chunks from a specific source (admin function)
    """
    from app.repositories.knowledge_repository import KnowledgeRepository
    
    knowledge_repo = KnowledgeRepository(db)
    
    try:
        deleted_count = knowledge_repo.delete_chunks_by_source(source_name)
        
        return {
            "message": f"Deleted knowledge source: {source_name}",
            "chunks_deleted": deleted_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete source: {str(e)}"
        )
