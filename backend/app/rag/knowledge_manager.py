import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.rag.ingestion import KnowledgeIngestionPipeline
from app.repositories.knowledge_repository import KnowledgeRepository
import logging

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """
    High-level interface for managing the knowledge base
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ingestion_pipeline = KnowledgeIngestionPipeline(db)
        self.knowledge_repo = KnowledgeRepository(db)
    
    async def setup_default_knowledge_base(self) -> Dict[str, Any]:
        """Setup default art learning content"""
        
        logger.info("Setting up default art knowledge base...")
        
        # Default art learning content
        art_basics_content = """
# Art Fundamentals

## Drawing Basics
Drawing is the foundation of all visual arts. It involves creating marks on a surface to represent objects, people, places, or ideas.

### Essential Drawing Tools:
- Pencils (2H, HB, 2B, 4B, 6B)
- Erasers (kneaded and regular)
- Drawing paper or sketchbooks
- Blending stumps
- Rulers and measuring tools

### Basic Drawing Techniques:
1. **Contour Drawing**: Drawing the outline or edges of objects
2. **Gesture Drawing**: Quick sketches capturing movement and energy
3. **Shading**: Using light and dark values to create form
4. **Cross-hatching**: Creating tone through intersecting lines
5. **Blending**: Smoothly transitioning between tones

## Color Theory
Understanding color is crucial for creating compelling artwork.

### Primary Colors:
- Red, Blue, Yellow - cannot be created by mixing other colors

### Secondary Colors:
- Orange (Red + Yellow)
- Green (Blue + Yellow) 
- Purple (Red + Blue)

### Color Properties:
1. **Hue**: The color itself (red, blue, etc.)
2. **Saturation**: The intensity or purity of the color
3. **Value**: How light or dark the color is

### Color Harmony:
- **Complementary**: Colors opposite on the color wheel
- **Analogous**: Colors next to each other on the color wheel
- **Triadic**: Three colors evenly spaced on the color wheel

## Composition
Composition is how elements are arranged in your artwork.

### Rule of Thirds:
Divide your canvas into nine equal sections with two horizontal and two vertical lines. Place important elements along these lines or at their intersections.

### Leading Lines:
Use lines to guide the viewer's eye through your composition.

### Balance:
- **Symmetrical**: Equal visual weight on both sides
- **Asymmetrical**: Different elements balanced through size, color, or placement

### Focal Point:
The main area of interest that draws the viewer's attention.

## Perspective
Perspective creates the illusion of depth and three-dimensional space.

### One-Point Perspective:
All lines converge to a single vanishing point on the horizon line. Good for drawing roads, hallways, or simple buildings.

### Two-Point Perspective:
Uses two vanishing points, typically for drawing corners of buildings or objects at an angle.

### Three-Point Perspective:
Adds a third vanishing point above or below, used for dramatic views looking up or down.

## Light and Shadow
Understanding light helps create realistic and dramatic artwork.

### Types of Light:
1. **Direct Light**: Strong, creates sharp shadows
2. **Indirect Light**: Soft, creates gentle shadows
3. **Ambient Light**: General surrounding light

### Shadow Types:
- **Cast Shadow**: Shadow thrown by an object
- **Form Shadow**: Shadow on the object itself
- **Core Shadow**: Darkest part of the form shadow
- **Reflected Light**: Light bounced back onto the shadowed area

## Practice Exercises for Beginners:

1. **Daily Sketching**: Draw something every day, even if just for 10 minutes
2. **Blind Contour Drawing**: Draw without looking at your paper
3. **Value Studies**: Practice shading simple geometric shapes
4. **Copy Master Artworks**: Learn techniques by studying great artists
5. **Life Drawing**: Draw from real objects, people, or scenes
6. **Color Mixing**: Experiment with creating different colors
7. **Perspective Exercises**: Draw simple boxes in different perspectives

## Common Beginner Mistakes to Avoid:

1. **Drawing too small**: Give yourself space to work
2. **Pressing too hard**: Start light and build up darkness gradually
3. **Not observing properly**: Look more than you draw
4. **Perfectionism**: Embrace mistakes as learning opportunities
5. **Skipping fundamentals**: Master basics before moving to complex subjects
6. **Not practicing regularly**: Consistency is more important than long sessions

## Building Your Art Skills:

### Progressive Learning Path:
1. Start with basic shapes and lines
2. Practice shading simple forms
3. Learn basic perspective
4. Study color theory
5. Practice composition
6. Develop your personal style

### Resources for Continued Learning:
- Art books and tutorials
- Online courses and videos
- Local art classes
- Art museums and galleries
- Practice drawing groups
- Art supply store workshops

Remember: Art is a journey, not a destination. Be patient with yourself and enjoy the process of learning and creating!
"""
        
        # Ingest the default content
        results = {}
        
        try:
            chunk_ids = await self.ingestion_pipeline.ingest_text(
                text=art_basics_content,
                source="art_fundamentals_guide",
                metadata={
                    "type": "educational_content",
                    "category": "art_basics",
                    "level": "beginner_to_intermediate"
                }
            )
            results["art_fundamentals"] = {
                "status": "success",
                "chunks_created": len(chunk_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest art fundamentals: {e}")
            results["art_fundamentals"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Add more default content as needed
        drawing_techniques_content = """
# Advanced Drawing Techniques

## Realistic Portrait Drawing

### Facial Proportions:
- The face is approximately 5 eyes wide
- Eyes are positioned halfway down the head
- Bottom of nose is halfway between eyes and chin
- Mouth is one-third of the way between nose and chin

### Drawing Eyes:
1. Start with basic almond shape
2. Add the iris (colored part)
3. Include the pupil (black center)
4. Add eyelashes and eyebrows
5. Show reflections and highlights

### Shading Techniques for Portraits:
- **Form Shading**: Follow the contours of the face
- **Soft Transitions**: Blend gradually between light and shadow
- **Reflected Light**: Don't make shadows completely black
- **Edge Control**: Vary hard and soft edges

## Landscape Drawing

### Creating Depth:
1. **Atmospheric Perspective**: Objects become lighter and less detailed in distance
2. **Overlapping**: Place objects in front of others
3. **Size Variation**: Make distant objects smaller
4. **Detail Reduction**: Less detail in background elements

### Tree Drawing Techniques:
- Start with basic trunk shape
- Add major branches
- Suggest foliage masses
- Add texture to bark
- Show light and shadow on leaves

### Water and Reflections:
- Water surface reflects objects
- Reflections are slightly darker than the object
- Add horizontal lines to show water movement
- Use vertical strokes for calm water reflections

## Advanced Shading Methods

### Hatching Patterns:
- **Parallel Lines**: Basic hatching for consistent tone
- **Cross-Hatching**: Intersecting lines for darker areas
- **Contour Hatching**: Lines follow the form of the object
- **Stippling**: Using dots to create tone

### Blending Techniques:
- **Finger Blending**: Smooth transitions
- **Stump Blending**: More controlled than fingers
- **Tissue Paper**: Soft, subtle blending
- **Brush Blending**: For very smooth transitions
"""
        
        try:
            chunk_ids = await self.ingestion_pipeline.ingest_text(
                text=drawing_techniques_content,
                source="advanced_drawing_techniques",
                metadata={
                    "type": "educational_content",
                    "category": "drawing_techniques",
                    "level": "intermediate_to_advanced"
                }
            )
            results["drawing_techniques"] = {
                "status": "success",
                "chunks_created": len(chunk_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest drawing techniques: {e}")
            results["drawing_techniques"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Get final stats
        stats = self.ingestion_pipeline.get_ingestion_stats()
        results["final_stats"] = stats
        
        logger.info("Default knowledge base setup completed")
        return results
    
    def get_knowledge_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of knowledge base"""
        
        stats = self.ingestion_pipeline.get_ingestion_stats()
        
        # Get sample content from each source
        source_samples = {}
        for source in stats["sources"][:5]:  # Limit to first 5 sources
            chunks = self.knowledge_repo.get_chunks_by_source(source, limit=1)
            if chunks:
                content_preview = chunks[0].content[:200] + "..." if len(chunks[0].content) > 200 else chunks[0].content
                source_samples[source] = {
                    "chunks_count": len(self.knowledge_repo.get_chunks_by_source(source, limit=1000)),
                    "preview": content_preview
                }
        
        return {
            "overview": stats,
            "source_samples": source_samples,
            "recommendations": self._get_knowledge_recommendations(stats)
        }
    
    def _get_knowledge_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Get recommendations for improving knowledge base"""
        recommendations = []
        
        if stats["total_chunks"] < 10:
            recommendations.append("Consider adding more educational content to improve AI responses")
        
        if stats["total_sources"] < 3:
            recommendations.append("Add diverse content sources for better coverage")
        
        if stats["total_chunks"] == 0:
            recommendations.append("Knowledge base is empty. Use setup_default_knowledge_base() to add initial content")
        
        return recommendations if recommendations else ["Knowledge base looks good!"]
    
    async def rebuild_knowledge_base(self, content_directory: Optional[str] = None) -> Dict[str, Any]:
        """Completely rebuild the knowledge base"""
        
        logger.info("Starting knowledge base rebuild...")
        
        # Clear existing knowledge (in a real app, you might want to backup first)
        sources = self.knowledge_repo.get_sources_list()
        total_deleted = 0
        for source in sources:
            deleted = self.knowledge_repo.delete_chunks_by_source(source)
            total_deleted += deleted
        
        logger.info(f"Cleared {total_deleted} existing chunks from {len(sources)} sources")
        
        # Rebuild with default content
        rebuild_results = await self.setup_default_knowledge_base()
        
        # If content directory provided, ingest files from there
        if content_directory and Path(content_directory).exists():
            try:
                directory_results = await self.ingestion_pipeline.ingest_directory(content_directory)
                rebuild_results["directory_ingestion"] = directory_results
            except Exception as e:
                rebuild_results["directory_ingestion"] = {"error": str(e)}
        
        rebuild_results["rebuild_summary"] = {
            "previous_chunks_deleted": total_deleted,
            "previous_sources_deleted": len(sources)
        }
        
        logger.info("Knowledge base rebuild completed")
        return rebuild_results
