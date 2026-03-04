#!/usr/bin/env python3
"""
Extended lesson generator for Art Buddy - Creates comprehensive art lessons
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.entities.models import Base, Lesson, QuizQuestion, KnowledgeChunk
from datetime import datetime
import uuid
import json

def generate_extended_lessons():
    """Generate comprehensive art lessons covering various topics and skill levels"""
    
    db: Session = SessionLocal()
    
    try:
        print("🎨 Generating extended art lessons...")
        
        # Advanced lessons for various art techniques
        extended_lessons = [
            {
                "title": "Advanced Shading and Light",
                "difficulty": "advanced",
                "lesson_type": "tutorial",
                "duration_minutes": 120,
                "content": """
# Advanced Shading and Light

Master the art of realistic shading by understanding how light interacts with different surfaces and forms.

## Understanding Light:
- **Key Light**: The main light source
- **Fill Light**: Secondary light that fills shadows
- **Rim Light**: Light that outlines the subject
- **Ambient Light**: General illumination in the environment

## Types of Shadows:
- **Cast Shadow**: Shadow thrown by an object
- **Form Shadow**: Shadow on the object itself  
- **Core Shadow**: The darkest area on a curved surface
- **Reflected Light**: Light bounced back from nearby surfaces

## Surface Materials and Light:
- **Matte Surfaces**: Soft, diffused reflections
- **Glossy Surfaces**: Sharp, mirror-like reflections
- **Metallic Surfaces**: High contrast highlights
- **Transparent Materials**: Light passes through with refraction

## Advanced Techniques:
1. **Atmospheric Perspective**: Objects become lighter and less detailed with distance
2. **Subsurface Scattering**: Light penetrating translucent materials like skin or leaves
3. **Occlusion Shadows**: Dark areas where surfaces meet
4. **Edge Control**: Making edges sharp or soft to control focus

## Exercise: Light Study
Set up a still life with multiple objects of different materials under strong directional lighting. 
Practice capturing the subtle differences in how light affects each surface.

## Materials Needed:
- Range of pencils (4H to 6B)
- Blending stumps
- Kneaded eraser
- White gel pen for highlights
- Tortillon for fine blending
                """
            },
            
            {
                "title": "Composition and Design Principles",
                "difficulty": "intermediate", 
                "lesson_type": "tutorial",
                "duration_minutes": 90,
                "content": """
# Composition and Design Principles

Learn to create visually compelling artwork through strong composition and design fundamentals.

## The Rule of Thirds:
- Divide your canvas into 9 equal sections
- Place important elements along the lines or at intersections
- Creates more dynamic and interesting compositions than centering

## Leading Lines:
- Use lines to guide the viewer's eye through your artwork
- Can be actual lines or implied through arrangement of elements
- Examples: roads, rivers, fence lines, shadows

## Visual Weight and Balance:
- **Symmetrical Balance**: Equal weight on both sides
- **Asymmetrical Balance**: Different elements that balance overall
- **Radial Balance**: Elements radiating from a central point

## Contrast and Emphasis:
- Use contrast in value, color, size, or texture to create focal points
- Avoid competing focal points that confuse the viewer
- Create hierarchy of importance in your composition

## Rhythm and Movement:
- Repetition of elements creates rhythm
- Variation prevents monotony
- Use direction and flow to create movement

## Unity and Harmony:
- All elements should work together as a cohesive whole
- Repeat colors, shapes, or textures throughout the piece
- Maintain consistent style and technique

## Exercise: Thumbnail Studies
Create 6-8 small thumbnail sketches (2"x3") exploring different compositions for the same subject. 
Vary the placement, scale, and arrangement to see which works best.

## Common Composition Mistakes:
- Centering everything
- Equal spacing of elements
- Cutting off important parts at canvas edges
- No clear focal point
- Competing elements of equal importance
                """
            },
            
            {
                "title": "Figure Drawing: Human Anatomy",
                "difficulty": "advanced",
                "lesson_type": "tutorial", 
                "duration_minutes": 150,
                "content": """
# Figure Drawing: Human Anatomy

Develop skills in drawing the human figure through understanding anatomy, proportions, and gesture.

## Basic Proportions:
- Average adult is 7-8 heads tall
- Shoulders are 2-3 head widths wide
- Arms reach to mid-thigh when extended
- Legs are approximately 4 heads long

## Skeletal Landmarks:
- **Skull**: Foundation for head proportions
- **Ribcage**: Oval shape, tilts and rotates with pose
- **Pelvis**: Bowl shape, supports the torso
- **Spine**: S-curve, provides balance and movement

## Major Muscle Groups:
- **Torso**: Pectorals, latissimus dorsi, abdominals
- **Arms**: Deltoids, biceps, triceps, forearms
- **Legs**: Quadriceps, hamstrings, calves, glutes

## Gesture Drawing:
- Capture the essence of a pose in 30 seconds to 2 minutes
- Focus on the line of action - the main flow of the pose
- Use confident, flowing lines
- Don't worry about details, capture the energy

## Proportional Techniques:
- **Sight-size Method**: Hold pencil at arm's length to measure
- **Comparative Measurement**: Compare sizes of different body parts
- **Envelope Method**: Draw the overall shape first, then add details

## Common Challenges:
- Drawing what you think you see vs. what's actually there
- Making heads too large or hands too small  
- Stiff, lifeless poses - remember the figure has weight and balance
- Avoiding difficult angles - practice foreshortening

## Progressive Exercise Plan:
1. **Gesture Studies** (30 seconds - 2 minutes each)
2. **Basic Structure** (5-10 minutes, focus on proportions)
3. **Detailed Study** (30+ minutes, include anatomy and shading)

## Study Recommendations:
- Use figure drawing references or attend life drawing sessions
- Study anatomy books (Bridgman, Loomis)
- Practice daily gesture drawings
- Draw from multiple angles and challenging poses
                """
            },
            
            {
                "title": "Watercolor Fundamentals",
                "difficulty": "beginner",
                "lesson_type": "tutorial",
                "duration_minutes": 100,
                "content": """
# Watercolor Fundamentals

Explore the beautiful, flowing medium of watercolor painting through essential techniques and color theory.

## Materials Needed:
- **Watercolor Paints**: Start with primary colors plus earth tones
- **Brushes**: Round brushes sizes 6, 10, 14 and a flat wash brush
- **Paper**: 140lb watercolor paper (minimum)
- **Water Containers**: Two jars (clean and dirty water)
- **Paper Towels**: For blotting and texture effects
- **Masking Tape**: To secure paper and create clean edges

## Basic Techniques:

### Wet-on-Wet:
- Apply water to paper first, then add paint
- Creates soft, diffused effects
- Great for skies, backgrounds, and atmosphere
- Less control but beautiful organic effects

### Wet-on-Dry:
- Apply paint to dry paper
- Creates sharp, defined edges
- Better control over paint placement
- Good for details and precise shapes

### Glazing:
- Apply thin, transparent layers over dry paint
- Each layer modifies the color beneath
- Build up rich, complex colors gradually
- Essential watercolor technique

## Color Mixing:
- **Primary Colors**: Cadmium Red, Ultramarine Blue, Cadmium Yellow
- **Secondary Colors**: Mix primaries (Orange, Green, Purple)
- **Earth Tones**: Burnt Sienna, Raw Umber, Yellow Ochre
- **Neutrals**: Mix complements to create grays and browns

## Water Control:
- **More Water**: Lighter, more transparent colors
- **Less Water**: More intense, saturated colors
- **Paper Dampness**: Controls how paint spreads
- **Timing**: When to add paint affects the result

## Common Techniques:
- **Variegated Wash**: Colors that blend into each other
- **Graded Wash**: Gradual transition from dark to light
- **Salt Technique**: Sprinkle salt into wet paint for texture
- **Splattering**: Flick brush for organic texture effects
- **Lifting**: Remove paint with clean, damp brush

## Exercise Progression:
1. **Color Swatches**: Practice mixing and test paint behavior
2. **Simple Washes**: Practice flat and graded washes
3. **Wet-in-wet flowers**: Simple blooms to understand control
4. **Landscape Study**: Combine techniques in a simple scene

## Common Mistakes:
- Using too little water (watercolor needs to flow)
- Working on inadequate paper (use proper watercolor paper)
- Overworking wet areas (let layers dry completely)
- Fear of dark values (watercolor can be bold too)
                """
            },
            
            {
                "title": "Digital Character Design",
                "difficulty": "intermediate",
                "lesson_type": "tutorial",
                "duration_minutes": 110,
                "content": """
# Digital Character Design

Create compelling original characters using digital tools and fundamental design principles.

## Character Design Pipeline:
1. **Concept and Research**: Define personality, role, setting
2. **Thumbnails**: Small, quick exploring different ideas
3. **Rough Sketches**: Develop promising designs further
4. **Refined Design**: Clean up proportions and details
5. **Color Studies**: Explore different color schemes
6. **Final Rendering**: Complete polished artwork

## Design Fundamentals:

### Silhouette:
- Strong, recognizable outline is crucial
- Should be readable as a solid black shape
- Vary the silhouette with props, clothing, hair, poses
- Test by filling your character with solid black

### Shape Language:
- **Circles**: Friendly, approachable, safe characters
- **Squares**: Stable, trustworthy, strong characters  
- **Triangles**: Dynamic, dangerous, aggressive characters
- Combine shapes for complex personalities

### Proportions:
- **Heroic**: 8-9 heads tall, idealized proportions
- **Realistic**: 7-8 heads tall, natural proportions
- **Stylized**: Exaggerated features for personality
- **Cartoon**: 3-6 heads tall, appealing and expressive

## Character Archetypes:
- **Hero**: Confident pose, idealized features, lighter colors
- **Villain**: Angular features, darker colors, threatening silhouette
- **Sidekick**: Smaller scale, rounder features, complementary to hero
- **Mentor**: Wise expression, distinguished features, mature proportions

## Costume and Props:
- Reflect character's job, personality, and background
- Consider practical aspects (how do they move/fight?)
- Use costume to show social class, culture, time period
- Props should support the character's role in story

## Color Theory for Characters:
- **Warm Colors**: Energetic, passionate, aggressive characters
- **Cool Colors**: Calm, mysterious, sad, or villainous characters
- **Complementary Schemes**: High contrast, eye-catching
- **Analogous Schemes**: Harmonious, unified feeling
- **Limited Palettes**: 3-5 colors maximum for cohesion

## Digital Techniques:
- **Layers**: Separate sketch, colors, shading for flexibility
- **Custom Brushes**: Create texture and interest
- **Color Modes**: Use Overlay, Multiply for lighting effects
- **Transform Tools**: Adjust proportions easily

## Exercise: Original Character:
1. Write a brief character description (personality, role, background)
2. Create 6 thumbnail silhouettes exploring different approaches
3. Choose best design and develop into refined sketch
4. Create 3 different color schemes
5. Complete final rendered character design

## Professional Tips:
- Study existing characters you admire
- Keep a reference library of costumes, poses, expressions
- Consider how character fits into their world/story
- Design characters that animators/artists want to draw repeatedly
                """
            },
            
            {
                "title": "Oil Painting Techniques",
                "difficulty": "advanced", 
                "lesson_type": "tutorial",
                "duration_minutes": 180,
                "content": """
# Oil Painting Techniques

Master the rich, versatile medium of oil painting through traditional and contemporary methods.

## Materials and Setup:

### Essential Colors:
- **Titanium White**: Primary white, good covering power
- **Ivory Black**: Warm black, mixes well
- **Ultramarine Blue**: Transparent, versatile blue
- **Cadmium Red Medium**: Opaque, vibrant red
- **Cadmium Yellow Medium**: Opaque, warm yellow
- **Yellow Ochre**: Earth tone, great for mixing
- **Burnt Sienna**: Warm brown, excellent for underpainting

### Brushes:
- **Filberts**: Versatile shape for most painting
- **Flats**: Good for blocking colors and edges
- **Rounds**: Detail work and fine lines
- **Fan Brushes**: Texture effects and blending
- **Palette Knives**: Mixing colors and impasto techniques

### Medium and Solvents:
- **Turpentine**: Thins paint, cleans brushes
- **Linseed Oil**: Increases flow and gloss
- **Medium**: Pre-mixed painting medium for consistency
- **Stand Oil**: Thick, levels brush strokes

## Fundamental Techniques:

### Fat Over Lean:
- Apply thicker paint (more oil) over thinner layers
- Prevents cracking as painting dries
- Start thin, gradually increase paint thickness
- Essential rule for permanent paintings

### Alla Prima (Wet-on-Wet):
- Complete painting in one session
- Paint directly without underpainting
- Colors blend and mix on canvas
- Spontaneous, fresh results

### Glazing:
- Transparent layers over dry paint
- Modifies color and creates depth
- Mix paint with medium for transparency
- Build up rich, luminous effects gradually

### Scumbling:
- Drag dry brush with little paint over texture
- Creates broken color effects
- Good for highlighting and atmospheric effects
- Useful for painting clouds, hair, grass textures

## Color Temperature:
- **Warm Colors**: Advance toward viewer (reds, oranges, yellows)
- **Cool Colors**: Recede into distance (blues, greens, purples)  
- **Relative Temperature**: Colors appear warm or cool depending on neighbors
- Use temperature shifts to create form and atmosphere

## Brushwork Techniques:
- **Broken Color**: Visible brushstrokes that vibrate optically
- **Blending**: Smooth transitions between colors
- **Impasto**: Thick paint application for texture
- **Dry Brush**: Minimal paint for subtle effects

## Painting Process:

### 1. Drawing/Sketch:
- Plan composition with light pencil or thin paint
- Establish major shapes and proportions
- Keep it simple, avoid excessive detail

### 2. Underpainting:
- Establish value structure in monochrome
- Use earth tones (burnt sienna, raw umber)
- Focus on light and shadow patterns
- Thin paint consistency

### 3. Color Blocking:
- Apply basic local colors in major shapes
- Work from dark to light generally
- Establish color temperature relationships
- Keep paint relatively thin still

### 4. Refining and Details:
- Develop forms with more specific colors
- Add texture and brushwork variety
- Increase paint thickness gradually
- Save smallest details for last

## Studio Practice:
- **Palette Organization**: Arrange colors consistently
- **Color Mixing**: Mix colors before applying to canvas
- **Brush Cleaning**: Clean between colors to maintain purity
- **Drying Time**: Oil paints dry slowly, plan accordingly

## Exercise: Simple Still Life
Set up 3-4 objects with strong lighting. Practice the complete process from underpainting to finished piece, focusing on clean color mixing and brushwork control.

## Advanced Concepts:
- **Optical Color Mixing**: Let eye blend colors rather than mixing on palette
- **Lost and Found Edges**: Vary edge quality for interest
- **Atmosphere**: Use color temperature and value for depth
- **Paint Quality**: Vary thick/thin application for visual interest
                """
            },
            
            {
                "title": "Drawing Dynamic Poses and Gestures",
                "difficulty": "intermediate",
                "lesson_type": "tutorial",
                "duration_minutes": 85,
                "content": """
# Drawing Dynamic Poses and Gestures

Capture life, energy, and movement in your figure drawings through gesture and dynamic posing.

## Understanding Gesture:
- **Gesture**: The essence of a pose, the feeling of movement
- **Line of Action**: Main flow line that runs through the pose
- **Rhythm**: How lines and forms flow throughout the figure
- **Weight**: How gravity affects the pose

## Finding the Line of Action:
1. Look for the main curve or angle of the spine
2. Extend this line through the head and limbs when possible
3. This line should express the energy of the pose
4. Avoid stiff, straight lines unless the pose demands it

## Dynamic Principles:

### Contrapposto:
- Weight shifts onto one leg
- Creates S-curve through the torso
- Shoulders and hips angle in opposition
- More natural, relaxed appearance

### Asymmetry:
- Avoid matching poses on both sides
- Vary arm and leg positions
- Creates more interesting, natural poses
- Suggests movement even in static poses

### Push and Pull:
- Show forces acting on the body
- Compression on weight-bearing side
- Extension on opposite side
- Visible in fabric folds and muscle tension

## Gesture Drawing Process:

### 30-Second Gestures:
- Capture only the essential action
- Use flowing, confident lines
- Don't lift pencil from paper often
- Focus on overall movement, not details

### 2-Minute Gestures:
- Establish basic proportions
- Define major muscle groups
- Add some volume to the gesture
- Still focus on energy over accuracy

### 5-10 Minute Studies:
- Develop structure and anatomy
- Add more specific details
- Check and correct proportions
- Begin to show light and shadow

## Common Gesture Mistakes:
- **Outlining**: Drawing edges instead of form
- **Stiffness**: Making figures look like mannequins
- **Symmetry**: Making both sides too similar
- **Rushing Details**: Adding features before establishing gesture
- **Timidity**: Using weak, uncertain lines

## Body Mechanics:

### Walking/Running:
- Opposite arm and leg move forward together
- Body leans slightly forward in direction of movement
- Contact foot bears full weight
- Lifting foot shows direction

### Reaching/Stretching:
- Entire body participates in the action
- Spine curves and extends
- Supporting leg stabilizes
- Shows clear intention and direction

### Twisting Actions:
- Shoulders and hips rotate in opposition
- Spine shows torsion through middle
- Arms and legs follow the twist
- Creates spiral energy through figure

## Emotional Gestures:
- **Confident**: Upright posture, expanded chest, firm stance
- **Defeated**: Slumped shoulders, lowered head, collapsed posture
- **Aggressive**: Forward lean, clenched fists, angular poses
- **Sad**: Curved spine, protected gestures, inward turn
- **Joyful**: Open gestures, lifted chest, expansive poses

## Practice Exercises:

### 1. Line of Action Studies:
Draw 20 figures using only single flowing lines. Focus purely on capturing the main action.

### 2. 30-Second Bursts:
Set timer and draw rapid gesture sketches. Don't allow time for careful observation.

### 3. Emotion Poses:
Draw the same figure showing different emotions through posture alone.

### 4. Action Sequences:
Draw a figure performing an action in 3-4 sequential poses.

## Using Reference:
- **Live Models**: Best for understanding weight and balance
- **Sports Photography**: Great for extreme dynamic poses
- **Dance/Performance**: Shows expressive, flowing movement
- **Everyday Actions**: Walking, sitting, reaching provide natural poses

## Memory and Construction:
- Practice drawing poses from memory after studying references
- Understand underlying structure, don't just copy surfaces
- Learn to construct poses from imagination
- Study how master artists solved similar problems
                """
            },
            
            {
                "title": "Landscape Painting in Acrylics",
                "difficulty": "intermediate",
                "lesson_type": "tutorial", 
                "duration_minutes": 125,
                "content": """
# Landscape Painting in Acrylics

Create stunning landscape paintings using the versatile, fast-drying medium of acrylic paint.

## Acrylic Advantages for Landscape:
- **Fast Drying**: Build up layers quickly
- **Weather Resistant**: Great for plein air painting
- **Versatile**: Can be diluted like watercolor or used thick like oil
- **Easy Cleanup**: Water-based, non-toxic
- **Color Stability**: Won't yellow or darken over time

## Essential Landscape Colors:
- **Titanium White**: For highlights and sky effects
- **Mars Black**: For deep shadows and mixing
- **Ultramarine Blue**: Sky and distant mountains
- **Phthalo Blue**: Intense blues for water and shadows
- **Cadmium Yellow Light**: Sunlight and bright foliage
- **Yellow Ochre**: Earth tones and autumn colors
- **Cadmium Red Medium**: Warm accents and sunset colors
- **Burnt Sienna**: Tree trunks, earth, warm shadows
- **Sap Green**: Foliage base color
- **Dioxazine Purple**: Atmospheric effects and shadows

## Landscape Elements:

### Sky Techniques:
- Start with lightest areas (usually top of sky)
- Work quickly while paint is wet for smooth blending
- Use horizontal brushstrokes for calm skies
- Add texture for dramatic cloud effects
- Remember: sky sets the mood for entire painting

### Clouds:
- **Cumulus**: Cotton-ball shapes with defined edges
- **Stratus**: Flat, layered formations
- **Cirrus**: Wispy, high-altitude clouds
- Show form through light and shadow
- Edges softer than solid objects

### Water Painting:
- Reflections are darker than the objects reflected
- Water surface breaks up reflections with horizontal lines
- Use horizontal brushstrokes to suggest water plane
- Add sparkles and highlights last
- Consider wind effects on surface texture

### Trees and Foliage:
- Start with overall silhouette shape
- Add major branch structure
- Build foliage in clusters, not individual leaves
- Vary greens by mixing with other colors
- Show light filtering through leaves

### Mountains and Distance:
- **Atmospheric Perspective**: Distant objects lighter and cooler
- Less detail in background elements
- Warm colors advance, cool colors recede
- Gradually reduce contrast with distance
- Sharp detail only in foreground

## Painting Process:

### 1. Composition Planning:
- Use viewfinder to select interesting composition
- Plan major shapes with thumbnail sketches
- Consider rule of thirds for horizon placement
- Identify primary focal point

### 2. Sky First:
- Paint sky completely before landscape elements
- Establishes lighting and mood
- Work wet-into-wet for smooth blending
- Save brightest whites for final highlights

### 3. Background to Foreground:
- Paint distant elements first
- Gradually work toward foreground
- Increase detail and contrast as you come forward
- Save sharpest details for very front

### 4. Final Details:
- Add texture and small details
- Brighten highlights
- Deepen darkest shadows  
- Step back frequently to assess overall effect

## Plein Air Tips:
- **Portable Setup**: Lightweight easel and limited palette
- **Changing Light**: Work quickly, note light direction
- **Weather Considerations**: Wind, temperature, UV protection
- **Simplified Approach**: Capture essence, not every detail
- **Color Notes**: Take photos for color reference

## Acrylic-Specific Techniques:

### Wet Blending:
- Work quickly before paint dries
- Use retarding medium to slow drying
- Mist painting lightly to keep workable
- Blend while both colors are wet

### Glazing:
- Thin transparent layers over dry paint
- Mix paint with glazing medium
- Modify colors and create atmosphere
- Build up rich, complex color effects

### Dry Brushing:
- Use minimal paint on brush
- Drag over textured surface
- Great for grass, tree bark, rock textures
- Creates broken color effects naturally

### Palette Knife Techniques:
- Apply thick paint for texture
- Mix colors directly on canvas
- Create interesting surface variety
- Good for rocks, clouds, foliage masses

## Exercise: Simple Landscape Study
Paint a basic landscape including sky, middle ground, and foreground elements. Focus on atmospheric perspective and light effects rather than fine detail.

## Common Landscape Mistakes:
- **Green Everything**: Vary greens with other colors
- **Equal Detail Throughout**: Reserve detail for focal areas
- **Flat Lighting**: Show strong light source and shadows
- **Harsh Edges Everywhere**: Vary soft and hard edges
- **Ignoring Atmosphere**: Use aerial perspective for depth
                """
            },
            
            {
                "title": "Character Expression and Emotions",
                "difficulty": "intermediate",
                "lesson_type": "tutorial",
                "duration_minutes": 95,
                "content": """
# Character Expression and Emotions

Master the art of conveying personality and emotions through facial expressions and body language.

## Facial Anatomy for Expression:

### Key Facial Features:
- **Eyebrows**: Primary indicator of emotion, highly mobile
- **Eyes**: Window to emotion, consider shape and gaze direction  
- **Mouth**: Second most expressive feature, shows many emotions
- **Cheeks**: Raise with genuine smiles, convey warmth
- **Forehead**: Wrinkles show concern, concentration, surprise

### Facial Muscles:
- **Orbicularis Oculi**: Muscles around eyes, genuine smiles
- **Levator Labii**: Lifts upper lip, disgust expressions
- **Zygomaticus**: Pulls mouth corners up, smiling
- **Frontalis**: Raises eyebrows, surprise and concern
- **Corrugator**: Furrows eyebrows, anger and concentration

## The Six Basic Emotions:

### Happiness:
- **Eyes**: Slight squint, crow's feet wrinkles
- **Mouth**: Corners turned up, may show teeth
- **Cheeks**: Raised, apple-shaped
- **Overall**: Open, relaxed features
- **Variations**: Laugh, grin, smirk, contentment

### Sadness:
- **Eyes**: Drooping upper eyelids, possible tears
- **Eyebrows**: Inner corners raised, creating triangle shape
- **Mouth**: Corners turned down, lower lip may protrude
- **Overall**: Drooping, wilted appearance
- **Variations**: Melancholy, grief, disappointment, despair

### Anger:
- **Eyes**: Narrowed, intense stare
- **Eyebrows**: Lowered and drawn together, sharp angle
- **Mouth**: Tightened, corners down, teeth may show
- **Jaw**: Clenched, facial tension visible
- **Variations**: Rage, annoyance, irritation, fury

### Fear:
- **Eyes**: Wide open, showing more white than normal
- **Eyebrows**: Raised and drawn together
- **Mouth**: Open, lips pulled back horizontally
- **Overall**: Tense, alert expression
- **Variations**: Terror, anxiety, worry, surprise-fear

### Surprise:
- **Eyes**: Wide open, eyebrows high
- **Mouth**: Dropped open, jaw relaxed  
- **Forehead**: Horizontal wrinkles from raised eyebrows
- **Overall**: Momentary, unstable expression
- **Variations**: Astonishment, shock, wonder

### Disgust:
- **Eyes**: Slightly narrowed
- **Nose**: Wrinkled, nostrils may flare
- **Mouth**: Upper lip raised, showing upper teeth
- **Overall**: Rejection, pulling away expression
- **Variations**: Contempt, disdain, revulsion

## Advanced Expression Concepts:

### Micro-Expressions:
- Brief, involuntary facial expressions
- Often show true feelings before conscious control
- Subtle but important for realistic character work
- Study photo references and slow-motion video

### Mixed Emotions:
- Real people rarely show pure single emotions
- Combine elements from different expressions
- Creates more complex, interesting characters
- Example: Sad smile (happiness + sadness)

### Cultural Variations:
- Expression intensity varies between cultures
- Eye contact norms differ globally
- Gesture meanings can vary significantly
- Research character's cultural background

## Body Language and Posture:

### Confident Expressions:
- **Posture**: Upright, shoulders back
- **Gestures**: Open hands, expansive movements
- **Stance**: Stable, balanced, feet planted
- **Head**: Held high, direct eye contact

### Defensive Expressions:
- **Posture**: Closed, shoulders hunched forward
- **Arms**: Crossed or protecting body
- **Stance**: Weight on back foot, ready to retreat
- **Head**: Lowered or turned away

### Aggressive Expressions:
- **Posture**: Forward lean, taking up space
- **Gestures**: Pointed fingers, clenched fists
- **Stance**: Wide, grounded, advancing
- **Head**: Forward thrust, direct stare

### Submission/Vulnerability:
- **Posture**: Small, compressed, shoulders inward
- **Arms**: Protective positions, self-hugging
- **Stance**: Unbalanced, weight shifting
- **Head**: Lowered, avoiding eye contact

## Age and Expression:

### Children:
- More exaggerated expressions
- Less emotional control, more pure emotions
- Larger eyes relative to face
- Softer, rounder facial features

### Adults:
- More subtle, controlled expressions
- Complex mixed emotions common
- Learned social expression masks
- Life experience shows in face

### Elderly:
- Permanent expression lines tell story
- May have reduced mobility in features
- Wisdom and experience in eyes
- Gravity effects on facial structure

## Drawing Expression Tips:

### Start with Basic Shapes:
- Circle for happy (round, open)
- Triangle for angry (sharp, pointed)  
- Oval for sad (drooping, elongated)
- Use shape language to support emotion

### Exaggerate for Clarity:
- Push expressions further than reality
- Especially important for animation/cartoon styles
- Clear communication more important than subtle realism
- Test readability at small sizes

### Consider Lighting:
- Dramatic lighting enhances emotion
- Up-lighting can make characters sinister
- Soft lighting creates gentle, pleasant moods
- Harsh shadows add drama and tension

## Exercise: Emotion Chart
Create a character sheet showing your character displaying 8-10 different emotions. Keep consistent facial structure while varying only the expression elements.

## Reference and Study:
- Mirror work: practice expressions yourself
- Photo references for subtle details
- Study master artists' approach to expression
- Observe real people in various emotional states
- Film and animation for dynamic expressions
                """
            }
        ]
        
        # Generate lesson objects and add to database
        lesson_objects = []
        for i, lesson_data in enumerate(extended_lessons):
            lesson = Lesson(
                id=str(uuid.uuid4()),
                title=lesson_data["title"],
                content=lesson_data["content"],
                difficulty=lesson_data["difficulty"],
                lesson_type=lesson_data["lesson_type"],  
                duration_minutes=lesson_data["duration_minutes"],
                created_at=datetime.utcnow()
            )
            lesson_objects.append(lesson)
            db.add(lesson)
            
        # Generate quiz questions for new lessons
        quiz_questions = [
            {
                "lesson": lesson_objects[0],  # Advanced Shading
                "question_text": "What is the darkest area on a curved surface called?",
                "question_type": "multiple_choice", 
                "options": ["Cast shadow", "Form shadow", "Core shadow", "Reflected light"],
                "correct_answer": "Core shadow",
                "explanation": "The core shadow is the darkest part of the form shadow on a curved surface, located between the lit area and the reflected light."
            },
            {
                "lesson": lesson_objects[1],  # Composition  
                "question_text": "According to the rule of thirds, where should important elements be placed?",
                "question_type": "multiple_choice",
                "options": ["Dead center", "Along the grid lines or intersections", "In the corners", "Randomly distributed"],
                "correct_answer": "Along the grid lines or intersections", 
                "explanation": "The rule of thirds suggests placing key elements along the imaginary lines that divide the image into nine sections, or at their intersections."
            },
            {
                "lesson": lesson_objects[2],  # Figure Drawing
                "question_text": "What is the main flow line that runs through a figure pose called?",
                "question_type": "multiple_choice",
                "options": ["Gesture line", "Line of action", "Contour line", "Construction line"],
                "correct_answer": "Line of action",
                "explanation": "The line of action is the main flow line that captures the essence and energy of a pose."
            },
            {
                "lesson": lesson_objects[3],  # Watercolor
                "question_text": "What happens when you apply paint to already wet paper?", 
                "question_type": "multiple_choice",
                "options": ["Creates hard edges", "Creates soft, diffused effects", "Paint doesn't stick", "Colors become muddy"],
                "correct_answer": "Creates soft, diffused effects",
                "explanation": "Wet-on-wet technique creates soft, organic, diffused effects as the paint spreads into the wet paper."
            },
            {
                "lesson": lesson_objects[4],  # Character Design
                "question_text": "Which shape language is associated with friendly, approachable characters?",
                "question_type": "multiple_choice", 
                "options": ["Triangles", "Squares", "Circles", "Rectangles"],
                "correct_answer": "Circles",
                "explanation": "Circular shapes are associated with friendly, safe, and approachable character personalities."
            }
        ]
        
        # Add quiz questions to database
        for quiz_data in quiz_questions:
            quiz = QuizQuestion(
                id=str(uuid.uuid4()),
                lesson_id=quiz_data["lesson"].id,
                question_text=quiz_data["question_text"], 
                question_type=quiz_data["question_type"],
                options=quiz_data["options"],
                correct_answer=quiz_data["correct_answer"],
                explanation=quiz_data["explanation"],
                created_at=datetime.utcnow()
            )
            db.add(quiz)
            
        # Generate additional knowledge chunks for RAG system
        knowledge_chunks = [
            {
                "content": "Advanced shading requires understanding how light interacts with different surfaces. The core shadow is the darkest area on a curved form, located between the lit surface and the reflected light. Cast shadows are thrown by objects onto other surfaces, while form shadows exist on the object itself.",
                "source": "Advanced Light and Shadow Guide",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "advanced_shading", "difficulty": "advanced"}
            },
            {
                "content": "Composition is the arrangement of visual elements in artwork. The rule of thirds divides the canvas into nine sections, with important elements placed along the lines or intersections. Leading lines guide the viewer's eye through the composition, while visual weight creates balance.",
                "source": "Composition Fundamentals Manual", 
                "chunk_index": 1,
                "chunk_metadata": {"topic": "composition", "difficulty": "intermediate"}
            },
            {
                "content": "Figure drawing captures the human form through understanding anatomy and gesture. The line of action is the main flow that runs through a pose, expressing its energy and movement. Contrapposto creates natural-looking poses through weight shifts and opposing angles.",
                "source": "Figure Drawing Techniques",
                "chunk_index": 1, 
                "chunk_metadata": {"topic": "figure_drawing", "difficulty": "advanced"}
            },
            {
                "content": "Watercolor painting relies on water control and transparency. Wet-on-wet technique applies paint to damp paper for soft effects, while wet-on-dry creates sharp edges. Glazing involves applying transparent layers over dry paint to build rich, complex colors.",
                "source": "Watercolor Methods Handbook",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "watercolor", "difficulty": "beginner"}
            },
            {
                "content": "Character design uses shape language to convey personality. Circles suggest friendly, safe characters; squares indicate stable, trustworthy types; triangles imply dynamic or dangerous personalities. Strong silhouettes should be readable as solid black shapes.",
                "source": "Character Design Principles",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "character_design", "difficulty": "intermediate"}
            },
            {
                "content": "Oil painting techniques include fat-over-lean application, where thicker paint goes over thinner layers. Alla prima involves completing a painting in one session, while glazing builds transparent layers for luminous effects. Scumbling creates broken color through dry brush techniques.",
                "source": "Oil Painting Methods",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "oil_painting", "difficulty": "advanced"}
            },
            {
                "content": "Dynamic poses show energy through the line of action and asymmetrical positioning. Contrapposto creates natural weight shifts, while gesture drawing captures movement essence in quick sketches. Body language communicates emotion through posture and positioning.",
                "source": "Dynamic Figure Art Guide",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "dynamic_poses", "difficulty": "intermediate"}
            },
            {
                "content": "Landscape painting benefits from understanding atmospheric perspective, where distant objects appear lighter and cooler. Acrylic paints offer versatility for both transparent and opaque techniques. Sky should be painted first to establish lighting and mood for the entire composition.",
                "source": "Landscape Painting Techniques",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "landscape_painting", "difficulty": "intermediate"}
            },
            {
                "content": "Facial expressions communicate emotions through specific muscle movements. The six basic emotions are happiness, sadness, anger, fear, surprise, and disgust. Eyebrows are the primary emotion indicators, while eyes and mouth provide supporting expression cues.",
                "source": "Character Expression Reference",
                "chunk_index": 1,
                "chunk_metadata": {"topic": "facial_expressions", "difficulty": "intermediate"}
            }
        ]
        
        # Add knowledge chunks to database  
        for chunk_data in knowledge_chunks:
            chunk = KnowledgeChunk(
                id=str(uuid.uuid4()),
                content=chunk_data["content"],
                source=chunk_data["source"],
                chunk_index=chunk_data["chunk_index"],
                chunk_metadata=chunk_data["chunk_metadata"],
                created_at=datetime.utcnow()
            )
            db.add(chunk)
            
        # Commit all changes
        db.commit()
        
        print(f"✅ Generated {len(extended_lessons)} comprehensive art lessons!")
        print(f"✅ Added {len(quiz_questions)} quiz questions!")  
        print(f"✅ Created {len(knowledge_chunks)} knowledge chunks for RAG system!")
        print("\n🎨 New Lessons Added:")
        for lesson in lesson_objects:
            print(f"   • {lesson.title} ({lesson.difficulty}) - {lesson.duration_minutes} min")
            
    except Exception as e:
        print(f"❌ Error generating lessons: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_extended_lessons()