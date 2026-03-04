#!/usr/bin/env python3
"""
Generate quizzes for lessons that don't have them
"""
from app.database import SessionLocal
from app.entities.models import Lesson, QuizQuestion
import uuid

db = SessionLocal()

try:
    # Define quizzes for each lesson
    quizzes = {
        # Portrait Drawing Fundamentals
        "Portrait Drawing Fundamentals": [
            {
                "question_text": "What is the most common proportion for adult face height to width?",
                "question_type": "multiple_choice",
                "options": [
                    "1:1 (equal height and width)",
                    "1.5:1 (height is 1.5 times the width)",
                    "2:1 (height is twice the width)",
                    "1:1.5 (width is 1.5 times the height)"
                ],
                "correct_answer": "1.5:1 (height is 1.5 times the width)",
                "explanation": "The typical adult face proportion is approximately 1.5:1 (height to width), though this can vary between individuals."
            },
            {
                "question_text": "Where should the eyes be positioned on the face?",
                "question_type": "multiple_choice",
                "options": [
                    "At the top third of the head",
                    "Halfway down the head",
                    "At the bottom third of the head",
                    "One-quarter down from the top"
                ],
                "correct_answer": "Halfway down the head",
                "explanation": "The eyes are typically positioned halfway down the total head height, a common beginner mistake is placing them too high."
            },
            {
                "question_text": "What is the 'Loomis method' used for in portrait drawing?",
                "question_type": "multiple_choice",
                "options": [
                    "Shading techniques",
                    "Constructing the head from different angles",
                    "Drawing realistic hair",
                    "Color theory for portraits"
                ],
                "correct_answer": "Constructing the head from different angles",
                "explanation": "The Loomis method is a construction technique for drawing the head from various angles using geometric shapes."
            }
        ],
        
        # Digital Art Basics
        "Digital Art Basics": [
            {
                "question_text": "What does 'DPI' stand for in digital art?",
                "question_type": "multiple_choice",
                "options": [
                    "Digital Pixel Input",
                    "Dots Per Inch",
                    "Display Pixel Intensity",
                    "Draw Point Index"
                ],
                "correct_answer": "Dots Per Inch",
                "explanation": "DPI (Dots Per Inch) measures the resolution of digital images. 300 DPI is standard for print, while 72 DPI is common for web."
            },
            {
                "question_text": "Which color mode is best for digital art intended for print?",
                "question_type": "multiple_choice",
                "options": [
                    "RGB (Red, Green, Blue)",
                    "CMYK (Cyan, Magenta, Yellow, Black)",
                    "HSB (Hue, Saturation, Brightness)",
                    "Grayscale"
                ],
                "correct_answer": "CMYK (Cyan, Magenta, Yellow, Black)",
                "explanation": "CMYK is the standard color mode for print because it matches how printers mix inks. RGB is for screens."
            },
            {
                "question_text": "What is a layer in digital art software?",
                "question_type": "multiple_choice",
                "options": [
                    "A type of brush",
                    "A separate transparent sheet that can hold artwork",
                    "A color palette",
                    "A file format"
                ],
                "correct_answer": "A separate transparent sheet that can hold artwork",
                "explanation": "Layers are like stacked transparent sheets that let you work on different parts of an artwork independently."
            },
            {
                "question_text": "What is the advantage of working with vector graphics over raster graphics?",
                "question_type": "multiple_choice",
                "options": [
                    "Better for photo editing",
                    "Scalable without losing quality",
                    "Smaller file sizes always",
                    "More realistic textures"
                ],
                "correct_answer": "Scalable without losing quality",
                "explanation": "Vector graphics use mathematical equations and can be scaled to any size without losing quality, unlike raster (pixel-based) images."
            }
        ],
        
        # Oil Painting Techniques
        "Oil Painting Techniques": [
            {
                "question_text": "What is the 'fat over lean' principle in oil painting?",
                "question_type": "multiple_choice",
                "options": [
                    "Always paint thick over thin layers",
                    "Apply layers with more oil content over layers with less oil",
                    "Paint light colors over dark colors",
                    "Use larger brushes before smaller ones"
                ],
                "correct_answer": "Apply layers with more oil content over layers with less oil",
                "explanation": "The 'fat over lean' rule prevents cracking by ensuring each layer has more oil (fat) than the one below it, allowing proper drying."
            },
            {
                "question_text": "Which medium is commonly used to thin oil paints and speed up drying?",
                "question_type": "multiple_choice",
                "options": [
                    "Water",
                    "Acrylic medium",
                    "Turpentine or odorless mineral spirits",
                    "Varnish"
                ],
                "correct_answer": "Turpentine or odorless mineral spirits",
                "explanation": "Turpentine or mineral spirits are traditional solvents for thinning oil paints and cleaning brushes. They also speed up drying."
            },
            {
                "question_text": "What is 'impasto' technique?",
                "question_type": "multiple_choice",
                "options": [
                    "Painting with very thin, transparent layers",
                    "Applying paint thickly so brush or palette knife strokes are visible",
                    "A watercolor technique",
                    "Spraying paint from a distance"
                ],
                "correct_answer": "Applying paint thickly so brush or palette knife strokes are visible",
                "explanation": "Impasto involves applying paint in thick layers, creating texture and dimension. Van Gogh famously used this technique."
            },
            {
                "question_text": "How long should you typically wait before varnishing a completed oil painting?",
                "question_type": "multiple_choice",
                "options": [
                    "Immediately after finishing",
                    "24 hours",
                    "1-2 weeks",
                    "6-12 months"
                ],
                "correct_answer": "6-12 months",
                "explanation": "Oil paintings should be completely dry before varnishing, which typically takes 6-12 months depending on paint thickness."
            }
        ],
        
        # Drawing Dynamic Poses and Gestures
        "Drawing Dynamic Poses and Gestures": [
            {
                "question_text": "What is the primary purpose of gesture drawing?",
                "question_type": "multiple_choice",
                "options": [
                    "To create finished, detailed drawings",
                    "To capture the energy, movement, and flow of a pose",
                    "To practice shading techniques",
                    "To memorize muscle anatomy"
                ],
                "correct_answer": "To capture the energy, movement, and flow of a pose",
                "explanation": "Gesture drawing focuses on capturing the essence, movement, and energy of a pose quickly, not on details."
            },
            {
                "question_text": "What is the 'line of action' in figure drawing?",
                "question_type": "multiple_choice",
                "options": [
                    "The outline of the figure",
                    "A curved line representing the flow and direction of the pose",
                    "The horizon line in the background",
                    "The centerline of symmetry"
                ],
                "correct_answer": "A curved line representing the flow and direction of the pose",
                "explanation": "The line of action is typically a curved line that captures the overall thrust and energy of a pose, guiding the entire drawing."
            },
            {
                "question_text": "How long are typical gesture drawing exercises?",
                "question_type": "multiple_choice",
                "options": [
                    "30 seconds to 5 minutes",
                    "20-30 minutes",
                    "1-2 hours",
                    "At least 3 hours"
                ],
                "correct_answer": "30 seconds to 5 minutes",
                "explanation": "Gesture drawings are quick studies, typically ranging from 30 seconds to 5 minutes, forcing artists to capture essence over detail."
            }
        ],
        
        # Landscape Painting in Acrylics
        "Landscape Painting in Acrylics": [
            {
                "question_text": "What is atmospheric perspective in landscape painting?",
                "question_type": "multiple_choice",
                "options": [
                    "Using a wide-angle lens",
                    "Objects becoming cooler, lighter, and less detailed as they recede",
                    "Painting from a high viewpoint",
                    "Using only blue tones"
                ],
                "correct_answer": "Objects becoming cooler, lighter, and less detailed as they recede",
                "explanation": "Atmospheric perspective creates depth by making distant objects appear lighter, bluer, and less distinct due to atmosphere."
            },
            {
                "question_text": "What is the advantage of acrylics over oils for landscape painting?",
                "question_type": "multiple_choice",
                "options": [
                    "They never dry",
                    "They dry quickly and can be painted over soon",
                    "They're always more expensive",
                    "They can only be used indoors"
                ],
                "correct_answer": "They dry quickly and can be painted over soon",
                "explanation": "Acrylics dry much faster than oils (minutes vs. days), making them ideal for plein air painting and building up layers quickly."
            },
            {
                "question_text": "What is 'plein air' painting?",
                "question_type": "multiple_choice",
                "options": [
                    "Painting indoors from photographs",
                    "Painting outdoors from direct observation",
                    "A specific style of abstract art",
                    "Using only primary colors"
                ],
                "correct_answer": "Painting outdoors from direct observation",
                "explanation": "Plein air (French for 'open air') means painting outdoors, directly observing the landscape and natural light."
            },
            {
                "question_text": "Where should the horizon line typically be placed in a landscape composition?",
                "question_type": "multiple_choice",
                "options": [
                    "Always in the dead center",
                    "At the top or bottom edge",
                    "About one-third from the top or bottom (rule of thirds)",
                    "It doesn't matter"
                ],
                "correct_answer": "About one-third from the top or bottom (rule of thirds)",
                "explanation": "Following the rule of thirds, placing the horizon at one-third creates more visually interesting compositions than centering it."
            }
        ],
        
        # Character Expression and Emotions
        "Character Expression and Emotions": [
            {
                "question_text": "Which facial features are most important for conveying emotion?",
                "question_type": "multiple_choice",
                "options": [
                    "Only the mouth",
                    "Only the eyes",
                    "The eyes and eyebrows together",
                    "Just the nose"
                ],
                "correct_answer": "The eyes and eyebrows together",
                "explanation": "The eyes and eyebrows working together are the most expressive features, communicating a wide range of emotions."
            },
            {
                "question_text": "What does the 'Duchenne smile' refer to?",
                "question_type": "multiple_choice",
                "options": [
                    "A fake smile using only the mouth",
                    "A genuine smile involving both mouth and eye muscles",
                    "An angry expression",
                    "A confused look"
                ],
                "correct_answer": "A genuine smile involving both mouth and eye muscles",
                "explanation": "A Duchenne smile is a genuine smile that activates both the mouth and the muscles around the eyes, creating crow's feet."
            },
            {
                "question_text": "What is 'squash and stretch' in animation and character expression?",
                "question_type": "multiple_choice",
                "options": [
                    "A type of color palette",
                    "Exaggerating facial features to emphasize emotion and movement",
                    "A lighting technique",
                    "A perspective method"
                ],
                "correct_answer": "Exaggerating facial features to emphasize emotion and movement",
                "explanation": "Squash and stretch is an animation principle that exaggerates deformation to create more dynamic, expressive characters."
            },
            {
                "question_text": "What are 'microexpressions'?",
                "question_type": "multiple_choice",
                "options": [
                    "Tiny face details",
                    "Brief, involuntary facial expressions revealing true emotions",
                    "Small cartoon characters",
                    "Miniature paintings"
                ],
                "correct_answer": "Brief, involuntary facial expressions revealing true emotions",
                "explanation": "Microexpressions are brief (1/25 to 1/5 second) involuntary facial movements that reveal genuine emotions people may be trying to hide."
            }
        ]
    }

    print("Generating quizzes for lessons...")
    print("="*80)
    
    for lesson_title, questions in quizzes.items():
        # Find the lesson
        lesson = db.query(Lesson).filter(Lesson.title == lesson_title).first()
        
        if not lesson:
            print(f"⚠️  Lesson not found: {lesson_title}")
            continue
        
        # Check if quiz already exists
        existing_quiz = db.query(QuizQuestion).filter(QuizQuestion.lesson_id == lesson.id).first()
        if existing_quiz:
            print(f"ℹ️  Quiz already exists for: {lesson_title}")
            continue
        
        print(f"\n📝 Creating quiz for: {lesson_title}")
        print(f"   Category: {lesson.category} | Difficulty: {lesson.difficulty}")
        
        # Create quiz questions
        for i, q_data in enumerate(questions, 1):
            quiz_question = QuizQuestion(
                id=uuid.uuid4(),
                lesson_id=lesson.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                points=1
            )
            db.add(quiz_question)
            print(f"   ✅ Question {i}: {q_data['question_text'][:60]}...")
        
        db.commit()
        print(f"   ✅ Created {len(questions)} questions for {lesson_title}")
    
    print("\n" + "="*80)
    print("Quiz Generation Summary:")
    print("="*80)
    
    # Get summary
    lessons_with_quizzes = db.query(Lesson).join(QuizQuestion).distinct().all()
    total_lessons = db.query(Lesson).count()
    total_quiz_questions = db.query(QuizQuestion).count()
    
    print(f"Total lessons: {total_lessons}")
    print(f"Lessons with quizzes: {len(lessons_with_quizzes)}")
    print(f"Total quiz questions: {total_quiz_questions}")
    
    print("\n✅ Quiz generation complete!")
    print("="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
