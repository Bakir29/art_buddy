#!/usr/bin/env python3
"""
Knowledge Base Setup Script for Art Buddy

This script helps initialize and manage the knowledge base for RAG functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import SessionLocal
from app.rag.knowledge_manager import KnowledgeManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_default_knowledge():
    """Setup default art learning knowledge base"""
    logger.info("Setting up default art knowledge base...")
    
    db = SessionLocal()
    try:
        knowledge_manager = KnowledgeManager(db)
        
        # Setup default knowledge base
        results = await knowledge_manager.setup_default_knowledge_base()
        
        logger.info("Setup Results:")
        for source, result in results.items():
            if isinstance(result, dict) and 'status' in result:
                if result['status'] == 'success':
                    logger.info(f"✅ {source}: {result.get('chunks_created', 0)} chunks created")
                else:
                    logger.error(f"❌ {source}: {result.get('error', 'Unknown error')}")
            else:
                logger.info(f"📊 {source}: {result}")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to setup knowledge base: {e}")
        raise
    finally:
        db.close()


async def get_knowledge_overview():
    """Get overview of current knowledge base"""
    logger.info("Getting knowledge base overview...")
    
    db = SessionLocal()
    try:
        knowledge_manager = KnowledgeManager(db)
        overview = knowledge_manager.get_knowledge_overview()
        
        logger.info("\n=== Knowledge Base Overview ===")
        stats = overview['overview']
        logger.info(f"Total Chunks: {stats['total_chunks']}")
        logger.info(f"Total Sources: {stats['total_sources']}")
        
        if stats['sources']:
            logger.info("\nSources:")
            for source in stats['sources']:
                logger.info(f"  - {source}")
        
        if overview['source_samples']:
            logger.info("\nSample Content:")
            for source, sample in overview['source_samples'].items():
                logger.info(f"  {source} ({sample['chunks_count']} chunks):")
                logger.info(f"    {sample['preview']}")
        
        if overview['recommendations']:
            logger.info("\nRecommendations:")
            for rec in overview['recommendations']:
                logger.info(f"  💡 {rec}")
        
        return overview
        
    except Exception as e:
        logger.error(f"Failed to get knowledge overview: {e}")
        raise
        
    finally:
        db.close()


async def rebuild_knowledge_base(content_dir=None):
    """Rebuild the entire knowledge base"""
    logger.info("Rebuilding knowledge base...")
    
    db = SessionLocal()
    try:
        knowledge_manager = KnowledgeManager(db)
        results = await knowledge_manager.rebuild_knowledge_base(content_dir)
        
        logger.info("\n=== Rebuild Results ===")
        for key, value in results.items():
            logger.info(f"{key}: {value}")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to rebuild knowledge base: {e}")
        raise
    finally:
        db.close()


def print_help():
    """Print usage instructions"""
    print("""
Art Buddy Knowledge Base Management

Usage:
  python setup_knowledge_base.py [command] [options]

Commands:
  setup     - Setup default art learning knowledge base
  overview  - Show current knowledge base overview
  rebuild   - Completely rebuild knowledge base
  help      - Show this help message

Options:
  --content-dir PATH  - Directory containing additional content files (for rebuild)

Examples:
  python setup_knowledge_base.py setup
  python setup_knowledge_base.py overview
  python setup_knowledge_base.py rebuild --content-dir ./art_content

Note: Ensure your database is running and .env is configured before running.
""")


async def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "setup":
            await setup_default_knowledge()
            logger.info("\n✅ Knowledge base setup completed!")
            
        elif command == "overview":
            await get_knowledge_overview()
            
        elif command == "rebuild":
            content_dir = None
            if "--content-dir" in sys.argv:
                idx = sys.argv.index("--content-dir")
                if idx + 1 < len(sys.argv):
                    content_dir = sys.argv[idx + 1]
            
            await rebuild_knowledge_base(content_dir)
            logger.info("\n✅ Knowledge base rebuild completed!")
            
        elif command == "help":
            print_help()
            
        else:
            logger.error(f"Unknown command: {command}")
            print_help()
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check configuration
    if not settings.openai_api_key:
        logger.warning("⚠️  OpenAI API key not configured. RAG will use mock responses.")
        logger.info("   Set OPENAI_API_KEY in your .env file for full functionality.")
    
    # Run the main function
    asyncio.run(main())