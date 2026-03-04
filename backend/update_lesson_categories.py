#!/usr/bin/env python3
"""
Update lessons with categories and progressive ordering
"""
from app.database import SessionLocal
from app.entities.models import Lesson
from sqlalchemy import text

db = SessionLocal()

try:
    # First, add the new columns if they don't exist
    print("Adding category and order_in_category columns...")
    try:
        db.execute(text("ALTER TABLE lessons ADD COLUMN category VARCHAR(100) DEFAULT 'general'"))
        db.execute(text("ALTER TABLE lessons ADD COLUMN order_in_category INTEGER DEFAULT 0"))
        db.commit()
        print("✅ Columns added successfully")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("ℹ️  Columns already exist, continuing...")
            db.rollback()
        else:
            raise

    # Define lesson categories and order (progressive from easiest to hardest within each category)
    lesson_updates = {
        # DRAWING CATEGORY - Progressive from basic to advanced
        "Introduction to Drawing": {"category": "drawing", "order": 1},
        "Perspective Drawing": {"category": "drawing", "order": 2},
        "Drawing Dynamic Poses and Gestures": {"category": "drawing", "order": 3},
        "Portrait Drawing Fundamentals": {"category": "drawing", "order": 4},
        "Figure Drawing: Human Anatomy": {"category": "drawing", "order": 5},
        
        # PAINTING CATEGORY - Progressive from basic to advanced
        "Watercolor Fundamentals": {"category": "painting", "order": 1},
        "Landscape Painting in Acrylics": {"category": "painting", "order": 2},
        "Oil Painting Techniques": {"category": "painting", "order": 3},
        
        # COLOR THEORY CATEGORY - Progressive
        "Color Theory Basics": {"category": "color_theory", "order": 1},
        "Advanced Shading and Light": {"category": "color_theory", "order": 2},
        
        # DIGITAL ART CATEGORY - Progressive
        "Digital Art Basics": {"category": "digital_art", "order": 1},
        "Digital Character Design": {"category": "digital_art", "order": 2},
        
        # DESIGN CATEGORY
        "Composition and Design Principles": {"category": "design", "order": 1},
        
        # CHARACTER ART CATEGORY
        "Character Expression and Emotions": {"category": "character_art", "order": 1},
    }

    print("\nUpdating lessons with categories and order...")
    for title, updates in lesson_updates.items():
        lesson = db.query(Lesson).filter(Lesson.title == title).first()
        if lesson:
            lesson.category = updates["category"]
            lesson.order_in_category = updates["order"]
            print(f"✅ Updated: {title:45} -> {updates['category']:15} (order: {updates['order']})")
        else:
            print(f"⚠️  Not found: {title}")

    db.commit()
    
    print("\n" + "="*80)
    print("Summary of lessons by category:")
    print("="*80)
    
    categories = db.execute(text("""
        SELECT category, COUNT(*) as count, 
               GROUP_CONCAT(difficulty) as difficulties
        FROM lessons 
        GROUP BY category 
        ORDER BY category
    """)).fetchall()
    
    for cat in categories:
        print(f"\n{cat[0].upper().replace('_', ' ')}:")
        lessons = db.query(Lesson).filter(Lesson.category == cat[0]).order_by(Lesson.order_in_category).all()
        for l in lessons:
            print(f"  {l.order_in_category}. {l.title:45} ({l.difficulty:12}) - {l.duration_minutes}min")
    
    print("\n" + "="*80)
    print("✅ Lesson categorization complete!")
    print("="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
