#!/usr/bin/env python3
"""
Seed script — 7 categories × 10 lessons × 5 quiz questions each (350 questions total).
Run:  python seed_data.py          # skips if data exists
      python seed_data.py --reset  # clears lessons/quizzes and re-seeds
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.entities.models import Base, User, Lesson, QuizQuestion, Progress, Reminder, KnowledgeChunk
from app.auth.security import get_password_hash
from datetime import datetime, timedelta
import uuid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lesson(title, content, difficulty, category, order, duration):
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "difficulty": difficulty,
        "category": category,
        "order_in_category": order,
        "lesson_type": "tutorial",
        "duration_minutes": duration,
        "created_at": datetime.utcnow(),
    }


def _q(lesson_id, question, options, correct, explanation):
    """correct is the exact string that appears in options."""
    return {
        "id": str(uuid.uuid4()),
        "lesson_id": lesson_id,
        "question_text": question,
        "question_type": "multiple_choice",
        "options": options,
        "correct_answer": correct,
        "explanation": explanation,
        "created_at": datetime.utcnow(),
    }


# ---------------------------------------------------------------------------
# Category 1 — Drawing  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def drawing_lessons():
    return [
        _lesson("Introduction to Drawing",
            """# Introduction to Drawing

Welcome to the world of drawing! This lesson lays the groundwork for everything that follows.

## What You Will Learn
- The purpose of sketching vs finished work
- How to hold a pencil for control vs expression
- Warm-up exercises every artist should do daily

## Materials
- Pencils: 2H (light), HB (all-purpose), 2B (dark)
- Cartridge or drawing paper
- Kneaded eraser

## Exercise 1 — Continuous Line
Draw simple objects (mug, shoe, hand) without lifting your pencil. This trains observation.

## Exercise 2 — Hatching Practice
Fill a 4×4 grid with different hatching directions: vertical, horizontal, diagonal, cross-hatch.

## Key Takeaway
Every master artist started with basic lines. Consistency over perfection.""",
            "beginner", "drawing", 1, 30),

        _lesson("Line Quality and Control",
            """# Line Quality and Control

The mark you make on paper carries meaning. Learn to master the full range of lines.

## Types of Lines
- **Thin/Light**: Sketching, underdrawing
- **Thick/Dark**: Emphasis, foreground objects
- **Broken**: Texture, distance
- **Confident**: Finished linework

## Pressure Control
Practice drawing lines from very light to very dark in a single stroke.

## Speed and Line Character
- Slow lines → controlled, mechanical
- Fast lines → dynamic, expressive

## Exercise
Draw 20 lines across a page at varying speeds and pressures. Label each 'slow', 'medium', or 'fast'.""",
            "beginner", "drawing", 2, 25),

        _lesson("Basic Shapes and Forms",
            """# Basic Shapes and Forms

All complex objects break down into simple shapes. Master these and you can draw anything.

## 2D Shapes
Circle, square, triangle, rectangle, ellipse

## 3D Forms
Sphere, cube, cylinder, cone, pyramid

## Drawing Forms with Volume
Shade one side darker to suggest a light source. Tonal contrast creates form.

## Construction Drawing
Block in complex objects with rectangles and circles first, then refine.

## Exercise
Pick 5 objects from your room. Identify their basic shapes. Sketch the shapes, then add detail.""",
            "beginner", "drawing", 3, 35),

        _lesson("Shading Fundamentals",
            """# Shading Fundamentals

Shading transforms flat outlines into solid three-dimensional objects.

## The Five Elements of Shading
1. **Highlight** — brightest point, often left white
2. **Light area** — softly lit surface
3. **Core shadow** — darkest area on the form itself
4. **Reflected light** — light bouncing back from nearby surfaces
5. **Cast shadow** — shadow thrown onto other surfaces

## Shading Techniques
- **Hatching**: Parallel lines
- **Cross-hatching**: Intersecting lines
- **Contour shading**: Lines follow the form
- **Blending**: Smooth gradient with a stump or finger

## Exercise
Draw a sphere lit from the upper-left. Apply all five shading elements.""",
            "beginner", "drawing", 4, 40),

        _lesson("Composition Basics",
            """# Composition Basics

Where you place elements is just as important as how well you draw them.

## The Rule of Thirds
Divide your canvas into a 3×3 grid. Place key subjects on intersections, not dead-centre.

## Leading Lines
Roads, fences, and rivers guide the viewer's eye toward the focal point.

## Framing
Arches, doorways, or tree branches frame the main subject naturally.

## Negative Space
The empty areas around and between subjects — use them intentionally.

## Exercise
Sketch the same still-life three ways: centred, rule-of-thirds, and with a strong leading line.""",
            "beginner", "drawing", 5, 35),

        _lesson("One-Point Perspective",
            """# One-Point Perspective

Create convincing depth with a single vanishing point on the horizon line.

## Key Terms
- **Horizon Line (HL)**: The viewer's eye level
- **Vanishing Point (VP)**: Where parallel lines converge
- **Orthogonal Lines**: Lines that travel to the VP

## When to Use It
Scenes viewed straight-on: hallways, roads, train tracks.

## Step-by-Step: Drawing a Room
1. Draw a horizon line and place a VP in the centre
2. Draw the back wall rectangle
3. Connect its corners to the VP
4. Define the floor, ceiling, and side walls

## Exercise
Draw a city street in one-point perspective with at least four buildings.""",
            "intermediate", "drawing", 6, 50),

        _lesson("Two-Point Perspective",
            """# Two-Point Perspective

Add a second vanishing point for corner views of objects and buildings.

## When to Use It
When you can see two sides of a building simultaneously.

## Step-by-Step: Drawing a Box
1. Draw horizon line with VP-Left and VP-Right at opposite ends
2. Draw a single vertical line (the nearest corner)
3. Connect its top and bottom to both VPs
4. Add back vertical edges to complete the box

## Common Mistake
Placing VPs too close together causes extreme distortion. Keep them wide apart.

## Exercise
Draw a cityscape with five buildings of varying heights in two-point perspective.""",
            "intermediate", "drawing", 7, 60),

        _lesson("Gesture Drawing",
            """# Gesture Drawing

Capture the energy and movement of the human figure in 30–60 seconds.

## What Is Gesture?
The overall action or flow of a pose — not anatomical details.

## The Line of Action
A single curved line running through the entire pose. All limbs flow from it.

## Timed Sessions
- 30 seconds: pure energy, no details
- 1 minute: gesture + major masses
- 5 minutes: gesture + structure + some anatomy

## Resources
Quickposes.com and Line of Action. Use 2B or soft charcoal for speed.

## Exercise
Complete a 20-pose session: 10 × 30-second, 5 × 1-minute, 5 × 2-minute poses.""",
            "intermediate", "drawing", 8, 45),

        _lesson("Still Life Drawing",
            """# Still Life Drawing

Drawing objects from observation sharpens every skill you have learned.

## Setting Up Your Still Life
- Arrange 3–5 objects with varied shapes and textures
- Use a single strong light source (desk lamp or window)
- Vary heights using books as platforms

## The Drawing Process
1. Lightly measure and block in proportions
2. Check angles and negative spaces
3. Refine outlines
4. Add shadows and midtones
5. Darken shadows, add final details

## Measuring Techniques
**Sight-sizing**: Hold your pencil at arm's length as a ruler against the actual object.

## Exercise
Spend 45–60 minutes drawing a fruit, a cup, and a book as a still life.""",
            "intermediate", "drawing", 9, 60),

        _lesson("Advanced Texture and Detail",
            """# Advanced Texture and Detail

Elevate your drawings by mastering how different surfaces catch light.

## Categories of Texture
- **Rough**: Stone, bark — varied hatching and broken lines
- **Smooth**: Glass, polished metal — gentle gradients, crisp highlights
- **Furry/Hairy**: Short strokes following the direction of growth

## Selective Detail
The focal point should be most detailed; edges should be softer. Never draw everything equally.

## Stippling
Creating tone and texture with dots. Denser dots = darker areas.

## Rendering Glass
1. Dark background behind the glass
2. Strong specular highlight
3. Slightly distorted contents showing refraction

## Exercise
Draw three objects with very different textures: glass, fabric, and rough stone.""",
            "advanced", "drawing", 10, 75),
    ]


def drawing_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "What is the main purpose of a warm-up exercise before drawing?",
           ["To fill the page", "To loosen the hand and improve control", "To test the pencil darkness", "To practise colour mixing"],
           "To loosen the hand and improve control",
           "Warm-up exercises prepare hand-eye coordination, reducing stiffness for more controlled subsequent work."),
        _q(l[0]["id"], "Which pencil grade produces the lightest lines?",
           ["6B", "2B", "HB", "2H"],
           "2H",
           "H pencils are harder and produce lighter, crisper lines. The higher the H number, the lighter the mark."),
        _q(l[0]["id"], "What does continuous line drawing train?",
           ["Colour mixing", "Observation and hand-eye coordination", "Brush control", "Perspective rules"],
           "Observation and hand-eye coordination",
           "Keeping the pencil on the paper forces you to observe the subject carefully without constant readjustment."),
        _q(l[0]["id"], "Which eraser type is best for lifting graphite without damaging paper?",
           ["Rubber eraser", "Kneaded eraser", "Sandpaper block", "Ink eraser"],
           "Kneaded eraser",
           "Kneaded erasers can be shaped to a fine point and lift graphite gently, preserving the paper surface."),
        _q(l[0]["id"], "Cross-hatching is best described as:",
           ["Dots placed close together", "Parallel lines in a single direction", "Intersecting sets of parallel lines", "Circular scribbles"],
           "Intersecting sets of parallel lines",
           "Cross-hatching uses two or more sets of parallel lines at different angles to build tone and texture."),
    ]

    qs += [
        _q(l[1]["id"], "Slow, deliberate lines tend to appear:",
           ["Expressive and gestural", "Controlled and mechanical", "Textured and rough", "Transparent"],
           "Controlled and mechanical",
           "Slow lines give the artist time to steer each mark, resulting in a more precise appearance."),
        _q(l[1]["id"], "Which line type is best for indicating objects in the distant background?",
           ["Thick dark lines", "Broken or light lines", "Gestural sweeping lines", "Triple-weight lines"],
           "Broken or light lines",
           "Lighter, thinner lines recede visually, suggesting objects in the middle or background."),
        _q(l[1]["id"], "What does varying pressure while drawing primarily control?",
           ["Paper colour", "Line weight (thickness and darkness)", "Pigment saturation", "Perspective depth"],
           "Line weight (thickness and darkness)",
           "Pressing harder creates darker, thicker lines; pressing lighter creates thinner, fainter marks."),
        _q(l[1]["id"], "A confident, fast line is most useful for:",
           ["Technical architecture diagrams", "Gesture and expressive work", "Precise measuring", "Stippling textures"],
           "Gesture and expressive work",
           "Fast lines capture energy and movement, ideal for gestural and dynamic compositions."),
        _q(l[1]["id"], "Underdrawing sketches are typically done with:",
           ["Heavy dark marks", "Light barely-visible lines", "Coloured ink", "Thick marker strokes"],
           "Light barely-visible lines",
           "Underdrawing acts as a guide; light lines are easy to erase or paint over without showing through the final work."),
    ]

    qs += [
        _q(l[2]["id"], "Which 3D form is most closely related to a 2D circle?",
           ["Cube", "Cylinder", "Sphere", "Pyramid"],
           "Sphere",
           "A sphere is the three-dimensional version of a circle — round in every direction."),
        _q(l[2]["id"], "In construction drawing, complex objects are first broken into:",
           ["Finished details", "Basic geometric shapes and forms", "Random curved lines", "Negative spaces only"],
           "Basic geometric shapes and forms",
           "Construction drawing uses simple shapes as placeholders before adding detail, ensuring correct proportions."),
        _q(l[2]["id"], "What creates the illusion of volume in a 3D form on 2D paper?",
           ["Bright colour", "Shading one side darker based on a light source", "Using a ruler", "Drawing multiple outlines"],
           "Shading one side darker based on a light source",
           "Tonal contrast from a light source convinces the eye of three-dimensionality."),
        _q(l[2]["id"], "A cylinder can be thought of as:",
           ["Two triangles and a rectangle", "Two circles connected by a curved surface", "A cube with rounded edges", "A cone on a sphere"],
           "Two circles connected by a curved surface",
           "The top and bottom are ellipses joined by a curved rectangular surface."),
        _q(l[2]["id"], "Why is identifying basic shapes useful to an artist?",
           ["It allows skipping the outline stage", "It ensures proportions are correct before adding detail", "It removes the need for shading", "It eliminates observation"],
           "It ensures proportions are correct before adding detail",
           "Blocking in simple shapes first establishes correct size and placement, making detail work much easier."),
    ]

    qs += [
        _q(l[3]["id"], "Which of the five shading elements is the darkest area ON the form?",
           ["Highlight", "Cast shadow", "Core shadow", "Reflected light"],
           "Core shadow",
           "The core shadow is the darkest band on the object itself, where light cannot reach at all."),
        _q(l[3]["id"], "Reflected light in shading refers to:",
           ["The brightest white spot", "Light bouncing back from a nearby surface into the shadow side", "The broad light area", "The edge of the cast shadow"],
           "Light bouncing back from a nearby surface into the shadow side",
           "Nearby surfaces bounce light back, slightly lightening the shadow side and preventing it from looking flat."),
        _q(l[3]["id"], "Contour shading means shading lines that:",
           ["Run straight across regardless of form", "Follow the curves and direction of the surface", "Are placed randomly", "Cross each other at 90 degrees"],
           "Follow the curves and direction of the surface",
           "Contour lines wrap around the form, reinforcing its three-dimensional shape."),
        _q(l[3]["id"], "A cast shadow is:",
           ["The darkness on the object itself", "The shadow thrown onto another surface by the object", "The reflected light area", "The highlight spot"],
           "The shadow thrown onto another surface by the object",
           "Cast shadows are produced when an object blocks the light source and throws a shadow onto surrounding surfaces."),
        _q(l[3]["id"], "Blending with a tortillon (blending stump) primarily creates:",
           ["Sharp hatched textures", "Smooth tonal gradients", "Broken line effects", "Stippled dot patterns"],
           "Smooth tonal gradients",
           "A tortillon smears graphite evenly, producing smooth transitions from light to shadow."),
    ]

    qs += [
        _q(l[4]["id"], "The Rule of Thirds divides the canvas into:",
           ["Four equal squares", "A 3×3 grid of nine equal parts", "Two halves", "A circular frame"],
           "A 3×3 grid of nine equal parts",
           "The Rule of Thirds grid creates four intersection points — placing subjects on these creates more dynamic compositions."),
        _q(l[4]["id"], "Leading lines in composition are used to:",
           ["Divide the image into equal sections", "Guide the viewer's eye toward the focal point", "Add texture to backgrounds", "Define shadow edges"],
           "Guide the viewer's eye toward the focal point",
           "Leading lines like roads and rivers direct attention naturally toward the main subject."),
        _q(l[4]["id"], "Negative space refers to:",
           ["Dark shadow areas", "The empty areas around and between subjects", "The background colour", "Areas with no linework"],
           "The empty areas around and between subjects",
           "Negative space is the 'empty' area; used intentionally, it shapes and balances the composition."),
        _q(l[4]["id"], "Placing the focal point dead-centre usually results in:",
           ["A dynamic composition", "A static, less engaging composition", "Better use of negative space", "Stronger leading lines"],
           "A static, less engaging composition",
           "Dead-centre placement feels static; off-centre placement (Rule of Thirds) creates more visual interest."),
        _q(l[4]["id"], "Framing in composition refers to:",
           ["Choosing a frame for the artwork", "Using elements within the scene to surround the subject", "Drawing a border", "Measuring canvas dimensions"],
           "Using elements within the scene to surround the subject",
           "Natural frames like arches or tree branches draw the eye inward and add depth."),
    ]

    qs += [
        _q(l[5]["id"], "In one-point perspective, how many vanishing points are used?",
           ["None", "One", "Two", "Three"],
           "One",
           "One-point perspective has a single vanishing point on the horizon line where all receding parallel lines converge."),
        _q(l[5]["id"], "The horizon line in perspective drawing represents:",
           ["The top of the canvas", "The viewer's eye level", "The ground plane", "The baseline of all objects"],
           "The viewer's eye level",
           "The horizon line corresponds to the viewer's eye level; its position determines the viewing angle."),
        _q(l[5]["id"], "Orthogonal lines in perspective drawing are:",
           ["Horizontal lines parallel to the horizon", "Lines that recede to the vanishing point", "Vertical lines on buildings", "Curved lines for organic shapes"],
           "Lines that recede to the vanishing point",
           "Orthogonal lines travel away from the viewer toward the vanishing point, creating depth."),
        _q(l[5]["id"], "One-point perspective is most suited for drawing:",
           ["A corner of a building at an angle", "A long straight road or hallway viewed head-on", "A bird's-eye map view", "Freeform organic landscape"],
           "A long straight road or hallway viewed head-on",
           "One-point perspective works best when looking directly at a scene that recedes straight back from the picture plane."),
        _q(l[5]["id"], "All receding lines in one-point perspective must pass through:",
           ["The horizon line midpoint", "The vanishing point", "The corner of the canvas", "The nearest object"],
           "The vanishing point",
           "All parallel lines that recede into space must converge at the single vanishing point."),
    ]

    qs += [
        _q(l[6]["id"], "Two-point perspective uses how many vanishing points?",
           ["One", "Two", "Three", "Four"],
           "Two",
           "Two vanishing points are placed on the horizon line — one left and one right."),
        _q(l[6]["id"], "Placing the two vanishing points very close together causes:",
           ["Subtle realistic depth", "Extreme distortion", "A flat unperspective drawing", "Softer shadows"],
           "Extreme distortion",
           "Close VPs produce highly exaggerated angles. Keeping them far apart reduces distortion."),
        _q(l[6]["id"], "In two-point perspective, vertical lines on a building are drawn:",
           ["Angling toward the VPs", "Perfectly vertical", "Horizontally across the page", "Curving with the horizon"],
           "Perfectly vertical",
           "In standard two-point perspective, vertical edges remain vertical — only horizontal edges recede to the VPs."),
        _q(l[6]["id"], "The 'nearest corner' of a box in two-point perspective is:",
           ["The vanishing point", "The single vertical line drawn first", "The horizon line", "The back edge of the box"],
           "The single vertical line drawn first",
           "Start by drawing the nearest vertical edge, then connect its top and bottom to both VPs to build the box."),
        _q(l[6]["id"], "Two-point perspective is best for drawing:",
           ["Scenes viewed perfectly head-on", "Corners, street intersections, and angled buildings", "Organic shapes like trees", "Flat overhead map views"],
           "Corners, street intersections, and angled buildings",
           "When you can see two sides of a building simultaneously, two-point perspective accurately captures that view."),
    ]

    qs += [
        _q(l[7]["id"], "Gesture drawing primarily focuses on capturing:",
           ["Precise anatomical details", "The energy, flow, and movement of a pose", "Accurate facial features", "Clothing and fabric folds"],
           "The energy, flow, and movement of a pose",
           "Gesture is about the overall action and emotion of the pose, not precision."),
        _q(l[7]["id"], "The 'line of action' in gesture drawing is:",
           ["The horizon line", "A single flowing line representing the main thrust of the pose", "The ground the figure stands on", "The silhouette outline"],
           "A single flowing line representing the main thrust of the pose",
           "The line of action runs from head to toe capturing the spine's curve and the pose's energy."),
        _q(l[7]["id"], "Which time limit is most commonly used for gesture warm-up poses?",
           ["10 minutes", "5 minutes", "30 seconds to 1 minute", "Never timed"],
           "30 seconds to 1 minute",
           "Very short timed poses force you to capture the essence of the gesture without getting caught in detail."),
        _q(l[7]["id"], "In a 30-second pose, you should prioritise:",
           ["Detailed facial features", "Correct finger placement", "The overall energy and line of action", "Accurate fabric texture"],
           "The overall energy and line of action",
           "With only 30 seconds, focus on the dominant line of action and biggest masses."),
        _q(l[7]["id"], "Why do artists practice gesture drawing regularly?",
           ["To memorise exact anatomy", "To improve speed, fluidity, and understanding of human movement", "To practise colour mixing", "To prepare canvas surfaces"],
           "To improve speed, fluidity, and understanding of human movement",
           "Regular gesture practice builds a mental library of poses and improves figure drawing confidence."),
    ]

    qs += [
        _q(l[8]["id"], "What lighting condition is ideal for a still life setup?",
           ["Overcast ambient light from all directions", "A single strong directional light source", "Natural daylight that changes throughout the day", "No direct lighting"],
           "A single strong directional light source",
           "A single direct light source creates clear highlights and shadows, making forms easier to understand and draw."),
        _q(l[8]["id"], "Sight-sizing is a technique used to:",
           ["Resize a finished drawing", "Measure proportions using the pencil held at arm's length", "Trace a projected image", "Estimate perspective angles"],
           "Measure proportions using the pencil held at arm's length",
           "Holding the pencil at arm's length allows direct comparison of sizes and angles against the subject."),
        _q(l[8]["id"], "When starting a still life drawing, you should first:",
           ["Add the darkest shadows immediately", "Block in overall proportions and placement lightly", "Draw the most detailed object first", "Fill the background completely"],
           "Block in overall proportions and placement lightly",
           "Establishing proportions lightly ensures everything fits the page before committing to detail."),
        _q(l[8]["id"], "Observing negative space in a still life helps you:",
           ["Choose a colour palette", "Check proportions by examining shapes between objects", "Apply surface texture", "Select a composition grid"],
           "Check proportions by examining shapes between objects",
           "The shapes between objects reveal proportion errors just as effectively as studying the objects themselves."),
        _q(l[8]["id"], "Varying the heights of objects in a still life arrangement is done to:",
           ["Replicate real storage methods", "Create visual interest and a sense of depth through overlapping", "Make outlines easier to draw", "Reduce shadow complexity"],
           "Create visual interest and a sense of depth through overlapping",
           "Varied heights create a more dynamic composition and introduce overlapping forms that suggest depth."),
    ]

    qs += [
        _q(l[9]["id"], "Selective detail means:",
           ["Drawing every area with equal care", "Applying the most detail to the focal point and less to edges", "Leaving the entire background blank", "Using only one shading technique"],
           "Applying the most detail to the focal point and less to edges",
           "High contrast and detail draw the eye; keeping peripheral areas simple emphasises the focal point."),
        _q(l[9]["id"], "To render a rough texture like stone or bark, use:",
           ["Smooth blended gradients", "Varied irregular hatching and broken edges", "Continuous even stippling only", "Flat unmodulated tone"],
           "Varied irregular hatching and broken edges",
           "Rough textures require uneven marks, broken outlines, and varied tones to replicate their appearance."),
        _q(l[9]["id"], "Stippling creates tone through:",
           ["Overlapping ink washes", "A density gradient of dots (more dots = darker)", "Hatched lines at 45 degrees", "Blended graphite"],
           "A density gradient of dots (more dots = darker)",
           "Stippling packs dots close for dark areas and spreads them for lighter areas."),
        _q(l[9]["id"], "When rendering transparent glass, the most important element is:",
           ["Uniform mid-tone", "A strong specular highlight and slightly distorted contents", "No shading since glass is clear", "A dark outline only"],
           "A strong specular highlight and slightly distorted contents",
           "Glass is identified by sharp specular reflections and the refraction (distortion) of what is seen through it."),
        _q(l[9]["id"], "When drawing fur or hair, individual strokes should:",
           ["Go in random directions", "Follow the direction the hair grows", "Be perfectly parallel and uniform", "Radiate outward from the centre only"],
           "Follow the direction the hair grows",
           "Strokes following growth direction look natural and create a convincing sense of flowing, directional texture."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 2 — Painting  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def painting_lessons():
    return [
        _lesson("Introduction to Watercolour",
            """# Introduction to Watercolour

Watercolour is one of the most accessible and rewarding painting media. Master its unique properties.

## Properties of Watercolour
- **Transparent**: Layers of paint let light pass through to the white paper below
- **Water-soluble**: Easy to thin and clean up with water
- **Unpredictable**: Wet-on-wet effects create beautiful, organic blooms

## Essential Materials
- Student or artist-grade watercolour paints
- Cold-press 140 lb (300 gsm) watercolour paper
- Round brushes (sizes 4, 8, 12)
- Two water jars (one clean, one for rinsing)

## Basic Technique — Flat Wash
Wet the paper, tilt at 15°, load the brush, and sweep horizontal strokes down the page. Let gravity pull the paint.

## Exercise
Paint three flat washes in your primary colours (red, yellow, blue) and let them dry fully before evaluating.""",
            "beginner", "painting", 1, 35),

        _lesson("Acrylic Painting Basics",
            """# Acrylic Painting Basics

Acrylics are versatile, fast-drying, and forgiving — perfect for beginners.

## Why Acrylics?
- Dry quickly (minutes to hours)
- Can mimic oil OR watercolour depending on dilution
- Water-soluble when wet, water-resistant when dry
- Affordable and widely available

## Painting Techniques
- **Blocking in**: Lay large areas of colour first
- **Wet-on-dry**: Apply paint to a dry surface for crisp edges
- **Dry brushing**: Nearly dry brush dragged across rough canvas for texture
- **Glazing**: Thin transparent layers to enrich colour

## Exercise
Paint a simple landscape using only three colours (sky, land, trees). Focus on blocking in large shapes first.""",
            "beginner", "painting", 2, 40),

        _lesson("Oil Painting Fundamentals",
            """# Oil Painting Fundamentals

Oil paint is the traditional medium of the Old Masters — rich, slow-drying, and endlessly blendable.

## Properties
- Slow drying time (days to weeks) — allows extensive blending
- Rich pigment and luminous colour
- Requires solvents (odourless mineral spirits) for thinning and cleaning

## Fat over Lean Rule
Each layer must contain more oil (fat) than the layer below it. Lean layers first, fat layers on top. Violating this causes cracking.

## Underpainting (Grisaille)
Paint the entire composition in neutral grey tones first to establish values before adding colour.

## Exercise
Complete a small (6×8 in.) monochromatic underpainting of a simple still life using raw umber and white.""",
            "beginner", "painting", 3, 50),

        _lesson("Colour Mixing for Painters",
            """# Colour Mixing for Painters

Understanding how to mix colours on the palette is as important as applying them to the canvas.

## The Limited Palette
Work with just 6–8 colours and learn to mix everything else. A good starter set:
- Titanium White, Ivory Black
- Cadmium Yellow, Yellow Ochre
- Cadmium Red, Alizarin Crimson
- Ultramarine Blue, Phthalo Blue

## Colour Temperature in Mixing
Every colour has a warm and cool version. Mixing two warm colours = pure vivid result. Mixing warm + cool = muted.

## Desaturation Methods
- Add the complement → muted, earthy
- Add grey or black → darker, less saturated

## Exercise
Mix a colour chart: fill a grid showing every primary mixed with every other primary at different ratios.""",
            "beginner", "painting", 4, 45),

        _lesson("Brush Techniques",
            """# Brush Techniques

The brush is your voice. Different strokes create entirely different effects and emotions.

## Brush Types
- **Round**: Versatile, pointed tip for lines and fills
- **Flat**: Sharp edges for geometry and broad strokes
- **Fan**: Blending and foliage effects
- **Filbert**: Soft edges and blending
- **Palette knife**: Thick impasto texture

## Loading the Brush
Full load → rich, juicy stroke. Partially loaded → broken, dry texture. Dry brush → rough texture.

## Marks and Strokes
- Stipple: dab the tip for foliage and texture
- Scumble: loosely scrub semi-opaque paint over a dry layer
- Calligraphic: vary pressure for thick-to-thin strokes

## Exercise
Fill a page with 12 different strokes using the same brush. Label each technique.""",
            "beginner", "painting", 5, 35),

        _lesson("Painting Light and Shadow",
            """# Painting Light and Shadow

Values (the lightness and darkness of colours) create the illusion of form and atmosphere.

## Value Scale
A value scale runs from pure white (1) to pure black (10). Most paintings use only 3–5 distinct value groups.

## The Three-Value System
- **Light**: Illuminated surfaces facing the light source
- **Mid-tone**: Transitional areas
- **Dark**: Shadow planes and cast shadows

## Squinting Test
Squint your eyes at the subject until detail disappears. Only large value shapes remain — those are what matter most.

## Painting Light Sources
- Key light: the main, brightest light
- Fill light: lower-intensity secondary light that softens shadows
- Rim light: light from behind that separates the subject from the background

## Exercise
Paint a simple sphere with only three values. Then refine with smooth transitions.""",
            "intermediate", "painting", 6, 55),

        _lesson("Landscape Painting",
            """# Landscape Painting

Landscapes teach atmosphere, perspective, and the behaviour of natural light.

## Aerial Perspective
Objects in the distance are:
- Lighter in value
- Less saturated (more grey/blue)
- Softer in edge quality

## Sky Painting
The sky is lighter and warmer near the horizon, darker and cooler at the zenith. Always paint sky before land.

## Designing a Landscape
Apply the Rule of Thirds: place the horizon line on one of the horizontal thirds — never in the centre.

## Edges in Landscape
- **Hard edges**: Sharp rocks, foreground details
- **Soft edges**: Clouds, distant trees, atmospheric haze

## Exercise
Paint a plein-air or photo-reference landscape in under one hour, focusing on accurate values.""",
            "intermediate", "painting", 7, 60),

        _lesson("Portrait Painting",
            """# Portrait Painting

Painting a convincing portrait combines colour theory, value structure, and anatomical understanding.

## Flesh Tones
Skin is NOT simply 'peach'. It contains warm oranges, cool pinks, yellow greens (near jawline), and purple (in shadow).

## Shadow Colours
Shadows on skin are typically cooler and more saturated in hue than the light areas.

## Painting the Eyes
Paint the eye socket shadow first as a single dark organic shape, then refine the eyelid, iris, and highlight.

## The Seven Planes of the Face
Forehead, brow ridge, nose, upper lip plane, lower lip plane, chin, cheeks — each catches light differently.

## Exercise
Paint a portrait study from a photograph focusing only on colour temperature: keep lights warm, shadows cool.""",
            "intermediate", "painting", 8, 70),

        _lesson("Texture in Painting",
            """# Texture in Painting

Texture adds tactile richness and visual interest that photographs and flat illustrations rarely achieve.

## Types of Texture
- **Physical texture** (impasto): Built up with thick paint, palette knife, or mixed media
- **Visual texture**: Simulated through brushwork and colour variation

## Impasto Technique
Apply paint thickly (≥ 1 cm) with a palette knife for dramatic raised marks. Best with oils or heavy-body acrylics.

## Sgraffito
Scratch into wet paint with a comb or knife to reveal underlayers — creates fine line texture.

## Mixed Media Texture
Embed sand, tissue paper, or modelling paste in the wet gesso ground before painting.

## Exercise
Create three 4×4 inch panels each demonstrating a different texture technique: impasto, sgraffito, and mixed media.""",
            "intermediate", "painting", 9, 60),

        _lesson("Abstract Painting Techniques",
            """# Abstract Painting Techniques

Break free from representation and let shape, colour, and texture carry the meaning.

## Principles of Abstract Art
- **Colour relationships**: How colours interact emotionally
- **Gestural mark-making**: The physical act of painting as expression
- **Composition**: Balance without recognisable objects
- **Repetition and rhythm**: Repeated shapes or marks create movement

## Approaches
- **Action painting**: Drip, splatter, or fling paint (Jackson Pollock style)
- **Hard-edge abstract**: Precise geometric shapes with clean edges (Mondrian-inspired)
- **Abstract Expressionism**: Emotional colour fields and gestural marks

## Starting Point
Work from an emotion or music piece, not a visual reference. Let the material guide decisions.

## Exercise
Paint an abstract piece inspired by a single emotion: use colour temperature, value, and mark-making to express it.""",
            "advanced", "painting", 10, 70),
    ]


def painting_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "What is the key defining property of watercolour paint?",
           ["It is opaque and covers previous layers", "It is transparent and relies on the white paper below", "It dries slowly and allows blending for hours", "It requires a solvent for thinning"],
           "It is transparent and relies on the white paper below",
           "Watercolour achieves its luminosity because light passes through the transparent paint and reflects back off the white paper."),
        _q(l[0]["id"], "To create a smooth flat wash in watercolour, you should:",
           ["Work on dry paper with a stiff brush", "Tilt the paper and sweep horizontal strokes letting gravity pull the bead", "Apply small circular strokes in all directions", "Use the driest possible brush"],
           "Tilt the paper and sweep horizontal strokes letting gravity pull the bead",
           "Tilting the paper causes the loaded bead of paint at the bottom of each stroke to flow downward, creating an even wash."),
        _q(l[0]["id"], "What weight (gsm) of watercolour paper is recommended to prevent buckling?",
           ["90 gsm", "150 gsm", "300 gsm", "600 gsm"],
           "300 gsm",
           "140 lb (300 gsm) paper is heavy enough to resist significant buckling when wet, making it ideal for watercolour."),
        _q(l[0]["id"], "The wet-on-wet watercolour technique produces:",
           ["Hard crisp edges", "Organic blooms and soft diffused edges", "Thick impasto texture", "Opaque flat colour"],
           "Organic blooms and soft diffused edges",
           "Wet paint dropped onto a wet surface flows and blooms unpredictably, creating soft organic shapes."),
        _q(l[0]["id"], "Why do artists use two water jars when painting with watercolour?",
           ["One for washing brushes, one kept clean for mixing pure washes", "One for warm water, one for cold", "One for each primary colour", "One for thinning, one for thickening"],
           "One for washing brushes, one kept clean for mixing pure washes",
           "Keeping one jar clean ensures that mixing water remains uncontaminated, preserving the purity of colour mixes."),
    ]

    qs += [
        _q(l[1]["id"], "What is a major advantage of acrylic paint over oil paint for beginners?",
           ["Acrylics dry much faster", "Acrylics have richer pigment than oils", "Acrylics require toxic solvents", "Acrylics cannot be thinned with water"],
           "Acrylics dry much faster",
           "Acrylics dry in minutes to hours, allowing faster reworking and layering without the long wait of oil paints."),
        _q(l[1]["id"], "The dry brushing technique in acrylic painting creates:",
           ["Smooth blended transitions", "Rough textured strokes on the canvas surface", "Thin transparent glazes", "Dripped splatter effects"],
           "Rough textured strokes on the canvas surface",
           "A nearly dry brush dragged quickly across a textured surface leaves broken, grainy marks that suggest rough texture."),
        _q(l[1]["id"], "Glazing with acrylics involves:",
           ["Heavy application of undiluted paint", "Thin transparent layers applied over a dry layer to enrich colour", "Scrubbing wet paint into the surface", "Mixing paint directly on the canvas"],
           "Thin transparent layers applied over a dry layer to enrich colour",
           "Glazing builds depth and luminosity by layering transparent colour, allowing light to interact with each layer."),
        _q(l[1]["id"], "In blocking in a composition, you should:",
           ["Start with the finest details in the focal point", "Lay large areas of colour to establish the overall composition first", "Mix every colour on the canvas directly", "Begin with the darkest shadows"],
           "Lay large areas of colour to establish the overall composition first",
           "Blocking in establishes the overall shapes and value structure before any detail is added."),
        _q(l[1]["id"], "Once dry, acrylic paint becomes:",
           ["Re-soluble in water", "Water-resistant and permanent", "Brittle and prone to cracking immediately", "Identical in appearance to oil paint"],
           "Water-resistant and permanent",
           "While acrylics are water-soluble when wet, the polymer binder creates a water-resistant film once fully dry."),
    ]

    qs += [
        _q(l[2]["id"], "The 'fat over lean' rule in oil painting means:",
           ["Thicker paint goes over thinner paint", "Each successive layer must contain more oil than the one below", "Lighter colours go over darker colours", "Fast-drying colours go on top"],
           "Each successive layer must contain more oil than the one below",
           "Lean (oil-poor) layers dry faster than fat (oil-rich) layers; applying fat under lean causes cracking as layers dry at different rates."),
        _q(l[2]["id"], "An underpainting in grisaille is:",
           ["A coloured sketch on coloured paper", "A full-value monochromatic underpainting usually in grey tones", "A final varnish coat", "A palette knife texture pass"],
           "A full-value monochromatic underpainting usually in grey tones",
           "Grisaille establishes the full value structure before colour is applied, making the painting process more systematic."),
        _q(l[2]["id"], "Why does oil paint dry slowly?",
           ["Its pigments contain no binder", "It cures through oxidation of the oil binder rather than evaporation", "It requires heat to dry", "The solvent evaporates very slowly"],
           "It cures through oxidation of the oil binder rather than evaporation",
           "Linseed and other oils undergo a chemical reaction (oxidative polymerisation) with air, a slow process that can take days or weeks."),
        _q(l[2]["id"], "Which solvent is recommended for thinning oil paint and cleaning brushes?",
           ["Water", "Rubbing alcohol", "Odourless mineral spirits", "Acetone"],
           "Odourless mineral spirits",
           "Odourless mineral spirits thin oil paint and clean brushes without the toxic fumes of traditional turpentine."),
        _q(l[2]["id"], "Starting an oil painting with raw umber underpainting is useful because:",
           ["Raw umber dries very slowly", "It establishes values quickly and dries faster than other oil colours", "It cannot be painted over with colour", "It seals the canvas permanently"],
           "It establishes values quickly and dries faster than other oil colours",
           "Raw umber is an earth pigment with less oil; it creates a lean, fast-drying underpainting that colour layers can safely go over."),
    ]

    qs += [
        _q(l[3]["id"], "Mixing two complementary colours together typically produces:",
           ["A vivid, saturated colour", "A muted, earthy, or neutral tone", "A lighter, tinted colour", "A pure primary colour"],
           "A muted, earthy, or neutral tone",
           "Complementary colours cancel each other out chromatically, producing neutral browns and greys when mixed."),
        _q(l[3]["id"], "A 'limited palette' in painting refers to:",
           ["Using only black and white", "Working with just 6–8 colours and mixing everything else", "Restricting yourself to one brush", "Painting on a very small canvas"],
           "Working with just 6–8 colours and mixing everything else",
           "A limited palette forces deeper understanding of colour mixing and produces naturally harmonious results."),
        _q(l[3]["id"], "Mixing a warm red with a cool blue tends to produce:",
           ["A vivid pure purple", "A slightly muted, less vibrant purple", "A bright orange", "A neutral green"],
           "A slightly muted, less vibrant purple",
           "Temperature differences between colours introduce subtle complementary bias, slightly desaturating the resulting mix."),
        _q(l[3]["id"], "To correctly mix a dark value without losing saturation, you should:",
           ["Add black to the colour", "Mix the colour's complement into it", "Add the complementary dark (e.g., dark blue to orange)", "Add white then rework the value"],
           "Add the complementary dark (e.g., dark blue to orange)",
           "Adding the right complementary dark darkens the value while preserving more saturation than mixing in black."),
        _q(l[3]["id"], "Titanium White is used in painting primarily to:",
           ["Increase transparency", "Lighten colour values and increase opacity", "Add warm temperature shifts", "Reduce drying time"],
           "Lighten colour values and increase opacity",
           "Titanium White is a strong opaque white ideal for lightening colours without making them too transparent."),
    ]

    qs += [
        _q(l[4]["id"], "Which brush type is best for painting precise geometric edges?",
           ["Round brush", "Fan brush", "Flat brush", "Filbert brush"],
           "Flat brush",
           "The flat brush has a sharp, squared-off edge ideal for straight, clean strokes and geometric shapes."),
        _q(l[4]["id"], "Dry brushing technique requires:",
           ["A fully loaded, dripping brush", "A brush with very little paint creating broken, textured strokes", "Wet paper or canvas surface", "A very soft round brush"],
           "A brush with very little paint creating broken, textured strokes",
           "The nearly dry brush skids across the textured surface, leaving irregular, grainy marks that suggest rough texture."),
        _q(l[4]["id"], "Stippling with a brush creates:",
           ["Smooth blended gradients", "Dot-like textured patterns ideal for foliage or rough surfaces", "Long sweeping gestural strokes", "Thin transparent glazes"],
           "Dot-like textured patterns ideal for foliage or rough surfaces",
           "Stippling dabs the brush tip repeatedly, building up texture through accumulated dot-like marks."),
        _q(l[4]["id"], "Scumbling is best described as:",
           ["Thinning paint heavily with solvent", "Loosely scrubbing semi-opaque paint over a dry layer", "Removing wet paint with a squeegee", "Applying paint with the fingers"],
           "Loosely scrubbing semi-opaque paint over a dry layer",
           "Scumbling drags semi-opaque paint lightly over a dry surface, allowing the underlayer to show through in places."),
        _q(l[4]["id"], "A filbert brush is most valued for:",
           ["Straight geometric lines", "Soft blended edges and natural-looking strokes", "Heavy impasto application", "Fine stipple texture"],
           "Soft blended edges and natural-looking strokes",
           "The filbert's rounded edge produces oval, petal-like strokes with naturally soft edges, ideal for blending and portraits."),
    ]

    qs += [
        _q(l[5]["id"], "What is a 'value' in the context of painting?",
           ["The monetary cost of a painting", "The lightness or darkness of a colour independent of its hue", "The level of detail in a painting", "The transparency of the paint"],
           "The lightness or darkness of a colour independent of its hue",
           "Value describes how light or dark a colour is on a scale from white to black, regardless of the hue."),
        _q(l[5]["id"], "Most successful paintings use how many distinct value groups?",
           ["At least 10", "Exactly 7", "3 to 5", "Only 2 (light and dark)"],
           "3 to 5",
           "Limiting yourself to 3–5 clear value groups creates bold, readable designs without muddy transitions."),
        _q(l[5]["id"], "The 'squinting test' in painting is used to:",
           ["Check brushwork texture up close", "Eliminate detail and reveal only the major light and dark shapes", "Evaluate colour temperature", "Test whether varnish is evenly applied"],
           "Eliminate detail and reveal only the major light and dark shapes",
           "Squinting blurs detail so only large value masses remain visible — these are the foundation of a strong painting."),
        _q(l[5]["id"], "A rim light (back light) is used in painting to:",
           ["Brighten the main focal area", "Separate the subject from the background", "Create cast shadows across the composition", "Warm the shadow areas"],
           "Separate the subject from the background",
           "Rim lighting creates a bright edge along the subject's silhouette, making it stand out clearly from the background."),
        _q(l[5]["id"], "In the three-value system, mid-tones refer to:",
           ["The lightest areas of the painting", "The darkest shadow planes", "Transitional areas between full light and full shadow", "The cast shadows on surrounding surfaces"],
           "Transitional areas between full light and full shadow",
           "Mid-tones bridge the transition between the clearly illuminated areas and the shadow planes."),
    ]

    qs += [
        _q(l[6]["id"], "Aerial perspective means that distant objects appear:",
           ["Larger and more saturated", "Lighter, less saturated, and with softer edges", "Darker with harder edges", "Identical in value to foreground objects"],
           "Lighter, less saturated, and with softer edges",
           "Atmosphere scatters light and reduces contrast, making distant objects lighter, bluer, and less distinct."),
        _q(l[6]["id"], "Where should the horizon line be placed according to the Rule of Thirds for landscapes?",
           ["Dead centre for maximum balance", "On one of the horizontal thirds, not in the middle", "At the very top of the canvas", "At the very bottom of the canvas"],
           "On one of the horizontal thirds, not in the middle",
           "Placing the horizon on a third (top third for sky emphasis, bottom third for land emphasis) creates a more dynamic split."),
        _q(l[6]["id"], "When painting the sky in a landscape, colour temperature near the horizon is typically:",
           ["Darker and cooler than the zenith", "Lighter and warmer than the zenith", "Identical throughout the sky", "Greener and more saturated"],
           "Lighter and warmer than the zenith",
           "The sky near the horizon has more atmosphere in the way, making it lighter and warmer (more orange/yellow); the zenith is deeper and cooler blue."),
        _q(l[6]["id"], "Hard edges in a landscape painting should be used for:",
           ["Distant mountains and clouds", "Foreground rocks and close-up details", "Soft atmospheric haze", "Elements at the same distance as the horizon"],
           "Foreground rocks and close-up details",
           "Objects close to the viewer have sharp, crisp edges; distant objects soften as aerial perspective blurs their outlines."),
        _q(l[6]["id"], "Painting plein air means:",
           ["Painting from imagination only", "Painting outdoors directly from the scene", "Painting with purely abstract intention", "Painting on a vertical wall surface"],
           "Painting outdoors directly from the scene",
           "Plein air (French for 'open air') refers to painting on location, directly observing the outdoor environment."),
    ]

    qs += [
        _q(l[7]["id"], "In portrait painting, shadow areas on skin are typically:",
           ["Warmer and more saturated than lit areas", "Cooler and often contain complementary hues", "Identical in temperature to lit areas", "Always painted with raw umber"],
           "Cooler and often contain complementary hues",
           "The shadowed side of the face cools slightly and may pick up ambient colour from the environment, creating natural colour variety."),
        _q(l[7]["id"], "The seven planes of the face concept helps a painter:",
           ["Select the right brush size", "Understand how different facets of the skull catch light differently", "Mix accurate skin tones only", "Establish the correct canvas proportions"],
           "Understand how different facets of the skull catch light differently",
           "Breaking the face into flat planes makes it easier to paint in terms of light, midtone, and shadow groupings."),
        _q(l[7]["id"], "When painting the eye, you should begin with:",
           ["The highlight and iris first", "The white of the eye (sclera) first", "The eye socket shadow as a single dark shape", "The eyelashes as fine lines"],
           "The eye socket shadow as a single dark shape",
           "Starting with the large shadow mass around the eye socket ensures correct value relationships before adding smaller refined details."),
        _q(l[7]["id"], "Skin tones in portrait painting contain:",
           ["Only peach or beige pigments", "A complex mix of warm oranges, cool pinks, yellows, and subtle greens or purples", "Only warm red and white", "Uniform values across light and shadow"],
           "A complex mix of warm oranges, cool pinks, yellows, and subtle greens or purples",
           "Skin is highly varied in colour temperature; successful portrait painters observe and mix this complexity rather than using a single skin-tone colour."),
        _q(l[7]["id"], "Keeping lights warm and shadows cool in a portrait study is a strategy for:",
           ["Reducing the number of colours needed", "Establishing clear colour temperature contrast that reads as natural light", "Making the portrait look abstract", "Simplifying value structure"],
           "Establishing clear colour temperature contrast that reads as natural light",
           "Warm light / cool shadow (or cool light / warm shadow) creates convincing, natural-looking illumination in portraiture."),
    ]

    qs += [
        _q(l[8]["id"], "Impasto technique involves:",
           ["Very thin, transparent glazes", "Thick application of paint that stands up in relief off the surface", "Scraping paint back to reveal the ground", "Sponging diluted paint onto texture"],
           "Thick application of paint that stands up in relief off the surface",
           "Impasto builds physical paint texture through heavy loading with a brush or palette knife, creating three-dimensional surface marks."),
        _q(l[8]["id"], "Sgraffito is a technique where you:",
           ["Apply thick paint with a fan brush", "Scratch into wet paint to reveal an underlying layer", "Build raised texture with modelling paste", "Apply sand to the wet paint surface"],
           "Scratch into wet paint to reveal an underlying layer",
           "Sgraffito (Italian: 'scratched') removes wet paint to expose the colour or value below, creating fine linear texture."),
        _q(l[8]["id"], "Which paint medium is best suited for thick impasto application?",
           ["Watercolour", "Thin-bodied acrylic ink", "Heavy-body acrylic or oil paint", "Gouache"],
           "Heavy-body acrylic or oil paint",
           "Heavy-body formulations hold their shape when applied thickly; thin or fluid paints will slump and lose texture."),
        _q(l[8]["id"], "Adding sand or modelling paste to gesso creates:",
           ["A smoother painting surface", "Physical ground texture that affects subsequent paint applications", "A transparent tinted ground", "A faster-drying, leaner ground"],
           "Physical ground texture that affects subsequent paint applications",
           "Adding coarse material to the ground creates a textured surface that physically breaks up brushstrokes, contributing to the final texture of the painting."),
        _q(l[8]["id"], "Visual texture (as opposed to physical texture) in painting is created through:",
           ["Thick impasto layers", "Brushwork and colour variation that simulates the appearance of texture", "Embedding objects in the paint surface", "Using a textured roller on wet paint"],
           "Brushwork and colour variation that simulates the appearance of texture",
           "Visual texture uses marks, patterns, and value variation to represent the appearance of texture without actually building up the paint surface."),
    ]

    qs += [
        _q(l[9]["id"], "In abstract painting, gestural mark-making refers to:",
           ["Precise geometric shape placement", "The physical act of applying paint as a form of expression", "Copying the gesture of another artwork", "Sketching the composition beforehand"],
           "The physical act of applying paint as a form of expression",
           "Gestural mark-making treats the application of paint itself as the expressive content, not the representation of an external subject."),
        _q(l[9]["id"], "Action painting (as pioneered by Pollock) is characterised by:",
           ["Precise geometric hard-edge shapes", "Dripping, flinging, or pouring paint in an energetic physical process", "Carefully observed still-life subjects", "Minimalist fields of flat colour"],
           "Dripping, flinging, or pouring paint in an energetic physical process",
           "Action painting emphasises the physical act and energy of creating the work, with the paint often applied through unconventional, dynamic methods."),
        _q(l[9]["id"], "Hard-edge abstract painting is characterised by:",
           ["Loose gestural marks and drips", "Blended soft edges throughout", "Precise geometric shapes with clean, sharp edges", "Impasto texture throughout"],
           "Precise geometric shapes with clean, sharp edges",
           "Hard-edge abstraction (associated with artists like Ellsworth Kelly) uses clean, geometric forms with no blending at the boundaries."),
        _q(l[9]["id"], "When starting an abstract painting without a visual reference, a useful approach is to:",
           ["Copy a famous abstract artwork", "Work from an emotion, concept, or music as inspiration", "Randomly apply paint with no intention", "Use only black and white to avoid colour decisions"],
           "Work from an emotion, concept, or music as inspiration",
           "Non-representational work still benefits from an internal starting point; emotion, music, or a concept guides colour, mark, and compositional choices."),
        _q(l[9]["id"], "Repetition and rhythm in abstract painting are created by:",
           ["Painting one large shape in the centre", "Using repeated shapes, marks, or colours that create visual movement across the canvas", "Applying random unconnected marks", "Using only one colour throughout"],
           "Using repeated shapes, marks, or colours that create visual movement across the canvas",
           "Repeating visual elements creates rhythm — the eye moves across the painting following the pattern, creating a sense of energy and flow."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 3 — Color Theory  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def color_theory_lessons():
    return [
        _lesson("The Colour Wheel",
            """# The Colour Wheel

The colour wheel is the foundation of all colour theory. Understanding it unlocks controlled, harmonious colour choices.

## Primary Colours
Red, Yellow, and Blue (RYB model) cannot be created by mixing other colours.

## Secondary Colours
Mixing two primaries creates a secondary:
- Red + Yellow = Orange
- Yellow + Blue = Green
- Blue + Red = Violet

## Tertiary Colours
Mixing a primary with an adjacent secondary creates 6 tertiary colours: Red-Orange, Yellow-Orange, Yellow-Green, Blue-Green, Blue-Violet, Red-Violet.

## Exercise
Draw a 12-segment colour wheel from memory, correctly placing all primary, secondary, and tertiary colours.""",
            "beginner", "color_theory", 1, 30),

        _lesson("Hue, Saturation, and Value",
            """# Hue, Saturation, and Value (HSV)

Every colour can be described using three dimensions: Hue, Saturation, and Value.

## Hue
The pure colour family — red, blue, yellow, etc. The name on the colour wheel.

## Saturation (Chroma)
How pure or vivid the colour is. 100% saturation = pure hue. 0% = grey.

## Value (Lightness)
How light or dark the colour is. Adding white increases value (tint). Adding black decreases value (shade).

## Tints, Shades, and Tones
- **Tint**: Hue + White
- **Shade**: Hue + Black
- **Tone**: Hue + Grey

## Exercise
Take one colour and create a 9-step chart: pure hue in centre, three tints left, three shades right, plus a toned version above and below.""",
            "beginner", "color_theory", 2, 35),

        _lesson("Colour Relationships and Harmonies",
            """# Colour Relationships and Harmonies

Colour harmonies are pre-built relationships on the colour wheel that reliably look pleasing together.

## Complementary
Colours directly opposite on the wheel (Red/Green, Blue/Orange). Maximum contrast. Use one as dominant, one as accent.

## Analogous
Three to five colours that sit adjacent on the wheel. Low contrast, naturally harmonious.

## Triadic
Three colours equidistant on the wheel (120° apart), e.g. Red, Yellow, Blue. Vibrant but balanced.

## Split-Complementary
A colour plus the two colours on either side of its complement. Less tension than pure complementary.

## Tetradic (Square/Rectangle)
Four colours forming a rectangle or square on the wheel. Rich, complex, requires careful balancing.

## Exercise
Create small colour studies using each of the five harmony types using the same warm orange as your base colour.""",
            "beginner", "color_theory", 3, 40),

        _lesson("Warm and Cool Colours",
            """# Warm and Cool Colours

Every colour has a temperature — warm or cool — that profoundly affects how we perceive and feel about it.

## Warm Colours
Reds, oranges, and yellows — associated with fire and sunlight. They advance visually, appearing closer.

## Cool Colours
Blues, greens, and violets — associated with water and shadow. They recede visually, appearing further away.

## Relative Temperature
All colours exist on a spectrum. Cadmium Yellow is warm; Lemon Yellow is cool. Ultramarine Blue is warm; Phthalo Blue is cool.

## Using Temperature in Composition
- Warm dominance = energetic, passionate
- Cool dominance = calm, melancholic
- Warm/cool contrast = vibration and depth

## Exercise
Paint the same simple scene twice: once with warm light + cool shadows, once with cool light + warm shadows.""",
            "beginner", "color_theory", 4, 35),

        _lesson("Colour Psychology",
            """# Colour Psychology

Colours carry powerful emotional associations. Understanding them helps you communicate intent to the viewer.

## Common Colour Associations
- **Red**: Passion, danger, urgency, energy
- **Orange**: Warmth, creativity, optimism
- **Yellow**: Happiness, caution, clarity
- **Green**: Nature, growth, calm, envy
- **Blue**: Trust, calm, sadness, depth
- **Violet**: Mystery, luxury, spirituality
- **Black**: Power, elegance, grief
- **White**: Purity, simplicity, emptiness

## Cultural Variation
Colour meanings vary by culture. White signifies mourning in some Asian cultures; red is auspicious in Chinese culture.

## Exercise
Create three small abstract compositions communicating: (1) danger, (2) peace, (3) joy — using only colour and simple shapes.""",
            "beginner", "color_theory", 5, 30),

        _lesson("Colour Temperature in Lighting",
            """# Colour Temperature in Lighting

The colour temperature of a light source dramatically changes the mood and appearance of everything in the scene.

## Colour Temperature Scale (Kelvin)
- Candlelight: ~1800K (very warm orange)
- Golden hour: ~3000K (warm gold)
- Noon daylight: ~5500K (neutral white)
- Overcast sky: ~7000K (cool blue-white)

## Painting Light Sources
Warm light = cool shadows. Cool light = warm shadows. This holds universally.

## Reflected Light
In the deepest shadow, a sphere often picks up warm-coloured reflected light from the ground beneath it — preventing shadows from becoming completely neutral grey.

## Exercise
Paint a sphere four times, each under a different colour temperature light (candlelight, golden hour, noon, overcast sky).""",
            "intermediate", "color_theory", 6, 50),

        _lesson("Simultaneous Contrast",
            """# Simultaneous Contrast

The same colour looks different depending on what surrounds it. This phenomenon is called simultaneous contrast.

## How It Works
Colours shift toward the complement of their surroundings. A grey square on a red background looks slightly green; on a green background it looks slightly red.

## Bezold Effect
Changing one colour in a repeating pattern changes the appearance of all surrounding colours.

## Value Contrast
A mid-grey appears lighter on black backgrounds and darker on white backgrounds.

## Practical Implications
When mixing colours for a painting, always judge them in context — not in isolation on the palette.

## Exercise
Create a grid of identical grey squares on 6 different coloured backgrounds and observe and document how each grey appears different.""",
            "intermediate", "color_theory", 7, 45),

        _lesson("Colour Mixing Models",
            """# Colour Mixing Models

Different contexts use different colour models. Understanding each prevents confusion and improves results.

## RYB (Subtractive — Traditional Art)
Red, Yellow, Blue primaries. Used by traditional painters. Not mathematically precise but intuitive.

## CMY/CMYK (Subtractive — Printing)
Cyan, Magenta, Yellow (+Black for printing). Mixing all three primaries = near black. Used in professional printing.

## RGB (Additive — Light/Screen)
Red, Green, Blue primaries. Used by screens and digital art tools. Mixing all three = white.

## Why Two Systems?
Subtractive mixing (pigment) absorbs wavelengths; adding colours removes light. Additive mixing (light) adds wavelengths; mixing colours adds light.

## Exercise
In a digital painting program, experiment with RGB sliders noting how different combinations produce different hues.""",
            "intermediate", "color_theory", 8, 40),

        _lesson("Value and Colour in Composition",
            """# Value and Colour in Composition

Value does the heavy lifting in any composition; colour refines and enhances it.

## Value First Principle
A painting with perfect colour but broken value structure will fail. A painting with perfect values but imperfect colour can still succeed.

## Notan
A Japanese concept — the beautiful interplay of light and dark shapes as a design principle. Reduce any image to two values; if it reads well, the composition is strong.

## Colour as Value
Every colour has an inherent value. Yellow is naturally light; violet is naturally dark. Keeping colours at their natural value preserves clarity.

## Value Dominance
Avoid equal portions of light and dark. Aim for about 70% one value, 30% the other. Add colour in the minority value for maximum impact.

## Exercise
Create a value-only (greyscale) thumbnail of a composition you're planning. Only begin adding colour once the value structure reads clearly.""",
            "intermediate", "color_theory", 9, 50),

        _lesson("Advanced Colour Strategies",
            """# Advanced Colour Strategies

Master artists use deliberate colour strategies to guide the viewer's eye and express mood at a sophisticated level.

## Gamut Mapping
Limit your colour palette to a small 'gamut' — a triangular region on the colour wheel. All colours stay within this region, ensuring automatic harmony.

## Chromatic Greys
Instead of mixing neutral greys from black and white, mix slightly chromatic greys from complementary colours. They vibrate with subtle colour.

## Colour Passage
A single colour repeated throughout a painting in small doses creates visual unity and rhythm.

## Colour Perspective (Temperature Recession)
Warm colours advance; cool colours recede. Use this to push and pull elements in space without relying solely on value contrast.

## Exercise
Design a painting using gamut mapping: choose a triangular gamut from the colour wheel and restrict every colour to within it.""",
            "advanced", "color_theory", 10, 65),
    ]


def color_theory_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "Which of the following are the three primary colours in the traditional RYB colour model?",
           ["Red, Green, Blue", "Cyan, Magenta, Yellow", "Red, Yellow, Blue", "Orange, Green, Violet"],
           "Red, Yellow, Blue",
           "In the traditional RYB colour model used by painters, the three primary colours are Red, Yellow, and Blue."),
        _q(l[0]["id"], "What colour results from mixing Red and Yellow?",
           ["Violet", "Orange", "Green", "Brown"],
           "Orange",
           "Red and Yellow are two primaries; their secondary mixture is Orange."),
        _q(l[0]["id"], "How many tertiary colours exist on a standard 12-segment colour wheel?",
           ["3", "6", "9", "12"],
           "6",
           "There are 6 tertiary colours — one between each primary and its adjacent secondary: Red-Orange, Yellow-Orange, Yellow-Green, Blue-Green, Blue-Violet, Red-Violet."),
        _q(l[0]["id"], "What is the secondary colour produced by mixing Blue and Yellow?",
           ["Violet", "Orange", "Green", "Brown"],
           "Green",
           "Blue + Yellow = Green. This is one of the three secondary colours."),
        _q(l[0]["id"], "Tertiary colours are produced by:",
           ["Mixing three primary colours", "Mixing two secondary colours", "Mixing a primary with an adjacent secondary", "Adding white to a primary colour"],
           "Mixing a primary with an adjacent secondary",
           "Tertiary colours sit between a primary and its neighbouring secondary on the colour wheel."),
    ]

    qs += [
        _q(l[1]["id"], "What does 'saturation' describe about a colour?",
           ["How light or dark it is", "How pure or vivid it is", "Its position on the colour wheel", "Its warm or cool quality"],
           "How pure or vivid it is",
           "Saturation (chroma) describes the purity or intensity of a colour; fully saturated = pure hue, desaturated = grey."),
        _q(l[1]["id"], "Adding white to a pure hue creates a:",
           ["Shade", "Tone", "Tint", "Complement"],
           "Tint",
           "A tint is a hue mixed with white, producing a lighter, less saturated version of the colour."),
        _q(l[1]["id"], "A 'shade' is created by:",
           ["Mixing a hue with white", "Mixing a hue with grey", "Mixing a hue with black", "Mixing two complementary colours"],
           "Mixing a hue with black",
           "A shade is a hue darkened by adding black."),
        _q(l[1]["id"], "If all three dimensions of colour are described by HSV, what does 'H' stand for?",
           ["Highlight", "Hue", "Harmony", "Haze"],
           "Hue",
           "H in HSV stands for Hue — the pure colour family or position on the colour wheel."),
        _q(l[1]["id"], "A 'tone' in colour theory is created by:",
           ["Adding black to a hue", "Adding white to a hue", "Adding grey to a hue", "Mixing two complements"],
           "Adding grey to a hue",
           "A tone is produced by mixing a hue with grey, reducing saturation without significantly shifting value."),
    ]

    qs += [
        _q(l[2]["id"], "Complementary colours are defined as:",
           ["Colours that sit adjacent on the colour wheel", "Colours directly opposite each other on the colour wheel", "Any two colours of similar saturation", "The three primary colours"],
           "Colours directly opposite each other on the colour wheel",
           "Complementary colours sit 180° apart on the colour wheel and produce maximum colour contrast."),
        _q(l[2]["id"], "An analogous colour scheme uses:",
           ["Three colours at 120° intervals", "Two colours opposite on the wheel", "Three to five colours adjacent on the wheel", "Four colours forming a rectangle or square"],
           "Three to five colours adjacent on the wheel",
           "Analogous colours sit next to each other on the wheel; they share common hue content and feel harmonious with low contrast."),
        _q(l[2]["id"], "An example of a triadic colour combination is:",
           ["Red, Orange, Red-Orange", "Red, Yellow, Blue", "Red, Cyan, Magenta", "Blue, Green, Blue-Green"],
           "Red, Yellow, Blue",
           "A triadic scheme uses three colours equidistant at 120° intervals. Red, Yellow, and Blue are the primary triad."),
        _q(l[2]["id"], "The split-complementary scheme differs from the complementary scheme by:",
           ["Using four colours instead of two", "Replacing one complement with the two colours flanking it", "Adding a neutral grey between the complements", "Desaturating both complementary colours"],
           "Replacing one complement with the two colours flanking it",
           "Split-complementary uses a base colour plus the two colours on either side of its direct complement, reducing tension."),
        _q(l[2]["id"], "A tetradic (square) colour scheme involves:",
           ["Two complementary pairs evenly spaced on the wheel", "Four adjacent analogous colours", "One colour plus three shades of it", "Two primaries and two secondaries chosen randomly"],
           "Two complementary pairs evenly spaced on the wheel",
           "A tetradic (square) scheme uses four colours forming a square on the wheel — effectively two complementary pairs."),
    ]

    qs += [
        _q(l[3]["id"], "Which of the following is a warm colour?",
           ["Blue-Violet", "Blue-Green", "Red-Orange", "Blue"],
           "Red-Orange",
           "Red-Orange is firmly in the warm half of the colour wheel, associated with fire and heat."),
        _q(l[3]["id"], "Cool colours tend to visually:",
           ["Advance and appear closer to the viewer", "Recede and appear further from the viewer", "Cancel out warm colours when placed adjacent", "Increase saturation of surrounding colours"],
           "Recede and appear further from the viewer",
           "Cool blues and violets visually recede, which is why skies and distant objects are painted cooler."),
        _q(l[3]["id"], "Among the two blues listed, which is relatively warmer?",
           ["Phthalo Blue", "Cerulean Blue", "Prussian Blue", "Ultramarine Blue"],
           "Ultramarine Blue",
           "Ultramarine Blue has a reddish-violet lean, making it warmer relative to Phthalo or Cerulean Blue."),
        _q(l[3]["id"], "In most natural lighting, shadows are painted with:",
           ["Warmer colours than the lit areas", "The same temperature as the lit areas", "Cooler colours than the lit areas", "Higher saturation than the lit areas"],
           "Cooler colours than the lit areas",
           "Under warm natural lighting, shadows lean cool; this warm light / cool shadow contrast creates a sense of depth and natural illumination."),
        _q(l[3]["id"], "A colour palette dominated by cool colours tends to convey:",
           ["Urgency and excitement", "Calm and melancholy", "Warmth and optimism", "High contrast and tension"],
           "Calm and melancholy",
           "Cool colours psychologically suggest stillness, depth, and sometimes sadness or introspection."),
    ]

    qs += [
        _q(l[4]["id"], "In colour psychology, the colour red is most commonly associated with:",
           ["Calm and trust", "Sadness and depth", "Passion, danger, and energy", "Nature and growth"],
           "Passion, danger, and energy",
           "Red is a high-arousal colour psychologically linked to passion, urgency, excitement, and danger."),
        _q(l[4]["id"], "Which colour is most associated with trust and calm in Western colour psychology?",
           ["Red", "Yellow", "Blue", "Orange"],
           "Blue",
           "Blue consistently rates as conveying trust, calm, and reliability in Western psychological and marketing research."),
        _q(l[4]["id"], "Colour meanings:",
           ["Are identical across all cultures globally", "Can vary significantly between different cultures", "Have no psychological effect on viewers", "Only apply to primary colours"],
           "Can vary significantly between different cultures",
           "For example, white signifies mourning in several Asian cultures but purity in many Western ones — cultural context is essential."),
        _q(l[4]["id"], "The colour yellow is most commonly associated with:",
           ["Mystery and spirituality", "Happiness, optimism, and caution", "Power and elegance", "Nature and growth"],
           "Happiness, optimism, and caution",
           "Yellow is linked to brightness, happiness, and optimism; its high visibility also makes it a standard colour for caution signs."),
        _q(l[4]["id"], "To convey a sense of 'danger' in an abstract composition using colour psychology, the most effective choice would be:",
           ["Soft lavender and sky blue", "Bright reds and blacks", "Pale yellow and light green", "White and light grey"],
           "Bright reds and blacks",
           "Red is strongly associated with danger and urgency, and the contrast against black amplifies that intensity."),
    ]

    qs += [
        _q(l[5]["id"], "A light source with a colour temperature of approximately 1800K would appear:",
           ["Cool blue-white", "Neutral white", "Warm orange-gold", "Greenish"],
           "Warm orange-gold",
           "At 1800K (candlelight level), light sources emit a deep warm orange-gold colour."),
        _q(l[5]["id"], "Warm light sources cast shadows that are:",
           ["Also warm", "Cool in temperature", "Neutral grey", "More saturated than the light areas"],
           "Cool in temperature",
           "Warm light produces cool shadows: the shadow areas are lit by ambient skylight which is cooler, creating a complementary temperature contrast."),
        _q(l[5]["id"], "The golden hour in photography and painting is prized because:",
           ["It produces a neutral, shadow-free light", "It creates extremely warm, directional light with long dramatic shadows", "It makes all colours appear cooler and more saturated", "It occurs when the sun is directly overhead"],
           "It creates extremely warm, directional light with long dramatic shadows",
           "The low sun angle at golden hour produces warm (~3000K) orange-gold light and long, dramatic shadows."),
        _q(l[5]["id"], "In painting a sphere, reflected light in the deepest shadow area is typically:",
           ["The same hue as the key light", "Warm, picked up from the illuminated ground below", "Black or pure neutral dark", "Cooler than the rest of the shadow"],
           "Warm, picked up from the illuminated ground below",
           "The ground near the sphere is lit by the warm key light; that light bounces back up into the underside of the sphere as reflected warm light."),
        _q(l[5]["id"], "An overcast sky produces a light with colour temperature of approximately 7000K, which appears:",
           ["Warm golden-yellow", "Neutral pure white", "Cool blue-white", "Deep red"],
           "Cool blue-white",
           "Overcast, diffuse skylight at ~7000K has a distinctly cool blue-white character."),
    ]

    qs += [
        _q(l[6]["id"], "Simultaneous contrast describes the phenomenon where:",
           ["Two colours mixed together cancel each other out", "The same colour appears different depending on surrounding colours", "Bright colours seem to vibrate when placed side by side", "Adding white to a colour changes its hue"],
           "The same colour appears different depending on surrounding colours",
           "Simultaneous contrast: a grey square surrounded by red will appear slightly green, and vice versa — the surrounding colour shifts perception."),
        _q(l[6]["id"], "A mid-grey square placed on a black background will appear:",
           ["Darker than it really is", "Lighter than it really is", "Identical to when placed on white", "Greenish due to complementary shift"],
           "Lighter than it really is",
           "High value contrast makes the grey appear lighter relative to the dark background; it looks darker on a white background."),
        _q(l[6]["id"], "The practical implication of simultaneous contrast for a painter is:",
           ["Colours should always be judged in isolation on the palette", "Colours should be judged in context to how they relate to surrounding colours", "Cool backgrounds always make warm colours appear warmer", "It only affects neutral greys, not hues"],
           "Colours should be judged in context to how they relate to surrounding colours",
           "Because surrounding colours shift our perception, a mix that looks right on the palette may need adjustment when placed on the canvas surrounded by other colours."),
        _q(l[6]["id"], "When a grey square is placed on a red background, the grey appears to shift toward:",
           ["Red", "Orange", "Blue", "Green"],
           "Green",
           "Simultaneous contrast shifts the perceived colour toward the complement of the background. The complement of red is green."),
        _q(l[6]["id"], "The Bezold Effect describes how:",
           ["Adding black to a hue makes it warmer", "Changing one colour in a repeating pattern changes the appearance of all surrounding colours", "Simultaneous contrast only works with neutrals", "Warm and cool colours always vibrate when adjacent"],
           "Changing one colour in a repeating pattern changes the appearance of all surrounding colours",
           "The Bezold Effect shows that a single change in one colour within a pattern can dramatically shift the visual appearance of all the other colours in that pattern."),
    ]

    qs += [
        _q(l[7]["id"], "In the RGB colour model, mixing Red, Green, and Blue light at full intensity produces:",
           ["Black", "Brown", "White", "Yellow"],
           "White",
           "RGB is an additive model; combining all three primaries at full intensity adds all wavelengths, producing white."),
        _q(l[7]["id"], "The CMYK model is primarily used for:",
           ["Digital screen displays", "Professional printing", "Traditional oil painting", "Stage lighting"],
           "Professional printing",
           "CMYK (Cyan, Magenta, Yellow, Black key) is the standard subtractive colour model used in printing."),
        _q(l[7]["id"], "In subtractive colour mixing (paint/pigment), mixing all three primary colours together produces:",
           ["White", "Bright secondary colour", "Near black or dark neutral", "A pure primary"],
           "Near black or dark neutral",
           "Mixing all three pigment primaries absorbs most wavelengths, resulting in a dark, near-black neutral."),
        _q(l[7]["id"], "Why is the RGB model called 'additive'?",
           ["Because you add pigments to the canvas", "Because combining coloured lights adds wavelengths, increasing brightness", "Because you must add a neutral to every mix", "Because more colours are available than in subtractive models"],
           "Because combining coloured lights adds wavelengths, increasing brightness",
           "Adding coloured light beams combines the wavelengths they emit; the more light added, the brighter and closer to white the result."),
        _q(l[7]["id"], "The traditional RYB model differs from the CMY model in that:",
           ["RYB uses fewer pigments", "RYB uses Red/Yellow/Blue primaries while CMY uses Cyan/Magenta/Yellow", "RYB allows for no colour mixing", "CMY is an additive model"],
           "RYB uses Red/Yellow/Blue primaries while CMY uses Cyan/Magenta/Yellow",
           "The traditional RYB model used by painters differs from the more accurate CMY subtractive model used in printing and colour science."),
    ]

    qs += [
        _q(l[8]["id"], "Which principle states that value structure is more critical to a painting's success than colour?",
           ["Gamut mapping", "The value first principle", "Simultaneous contrast", "Chromatic grey principle"],
           "The value first principle",
           "Value first: a painting with strong values and poor colour choices will still read clearly; the reverse is rarely true."),
        _q(l[8]["id"], "Notan is a concept from Japanese aesthetics that refers to:",
           ["Harmony of warm and cool temperatures", "The beautiful design created by light and dark shapes alone", "Saturation control in colour mixing", "The use of a limited palette"],
           "The beautiful design created by light and dark shapes alone",
           "Notan (Japanese: light-dark) is the design principle of using two values to create powerful, balanced compositions."),
        _q(l[8]["id"], "Yellow is naturally a light-valued colour on the colour wheel. Painting yellow at a very dark value would:",
           ["Look natural and correct", "Appear unnatural and create confusion in value structure", "Increase its perceived saturation", "Have no effect on composition clarity"],
           "Appear unnatural and create confusion in value structure",
           "Each hue has a natural value; forcing it far from that natural value creates visual dissonance and weakens clarity."),
        _q(l[8]["id"], "The ideal ratio for value distribution (light vs dark) in a composition is approximately:",
           ["50% light, 50% dark", "70% one value, 30% the other", "Equal thirds of light, mid, and dark", "90% light, 10% dark always"],
           "70% one value, 30% the other",
           "A 70/30 dominance ratio prevents a monotone or chaotic equal split, creating clear visual hierarchy."),
        _q(l[8]["id"], "An artist creating a value thumbnail before starting a colour painting is:",
           ["Wasting time that could be spent on colour", "Ensuring the composition reads clearly in terms of light and dark before colour is introduced", "Testing the canvas surface", "Checking for drawing accuracy"],
           "Ensuring the composition reads clearly in terms of light and dark before colour is introduced",
           "Value thumbnails let you solve the core compositional problem in minutes before investing time in a full colour painting."),
    ]

    qs += [
        _q(l[9]["id"], "Gamut mapping in painting means:",
           ["Using every colour on the colour wheel equally", "Restricting all colours in a painting to a limited triangular region of the colour wheel", "Mapping each object to a specific colour family", "Using only pure hues with no tints or shades"],
           "Restricting all colours in a painting to a limited triangular region of the colour wheel",
           "Gamut mapping constrains your colour selection to a defined region, guaranteeing automatic colour harmony across the painting."),
        _q(l[9]["id"], "A 'chromatic grey' is different from a neutral grey because:",
           ["It contains a subtle hue lean rather than being purely neutral", "It is always lighter than neutral grey", "It requires a digital colour picker to achieve", "It cannot be mixed from paint"],
           "It contains a subtle hue lean rather than being purely neutral",
           "Chromatic greys are mixed from complementary colours rather than black and white, resulting in greys that have subtle warmth or coolness."),
        _q(l[9]["id"], "Colour passage in painting refers to:",
           ["The gradual transition from one colour temperature to another", "A single colour repeated throughout a painting to create visual unity", "The route the viewer's eye takes through the composition", "The process of applying colour in glazing layers"],
           "A single colour repeated throughout a painting to create visual unity",
           "Colour passage ties the composition together by echoing one colour note in multiple places, creating rhythmic visual unity."),
        _q(l[9]["id"], "Colour perspective uses warm and cool temperature to:",
           ["Make all colours appear more saturated", "Push warm colours forward and cool colours back in space", "Neutralise colour conflicts in a composition", "Create equal visual weight across the painting surface"],
           "Push warm colours forward and cool colours back in space",
           "Warm colours psychologically advance while cool colours recede, giving the painter a powerful tool for creating spatial depth beyond value alone."),
        _q(l[9]["id"], "An artist who uses only chromatic greys instead of black-and-white neutral greys achieves:",
           ["Less saturation overall", "Subtly vibrating, colour-rich neutrals that harmonise with the rest of the palette", "Identical results to using standard grey", "Flatter, less interesting mid-tones"],
           "Subtly vibrating, colour-rich neutrals that harmonise with the rest of the palette",
           "Chromatic greys carry a subtle hue note that relates to the painting's palette, creating richer, more interesting mid-tones than pure black-and-white greys."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 4 — Digital Art  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def digital_art_lessons():
    return [
        _lesson("Introduction to Digital Art Tools",
            """# Introduction to Digital Art Tools

Digital art combines artistic skill with software. Understanding your tools is the essential first step.

## Hardware
- **Drawing tablet**: Wacom, Huion, or XP-Pen. Pressure-sensitive stylus replaces the mouse.
- **Screen tablet**: Display tablet lets you draw directly on-screen.
- **iPad + Apple Pencil**: Excellent portable setup with Procreate.

## Software Options
- **Photoshop**: Industry standard for photo editing and digital painting
- **Procreate**: iPad-first, intuitive for illustration
- **Clip Studio Paint**: Popular for illustration and manga
- **Krita**: Free and open-source, full-featured

## Key Interface Concepts
- Layers panel, brush engine, colour picker, transform tools
- Keyboard shortcuts dramatically speed up workflow

## Exercise
Set up your software, create a new canvas (2000 × 2000 px, 300 dpi) and practice making strokes with pressure variation.""",
            "beginner", "digital_art", 1, 35),

        _lesson("Understanding Layers",
            """# Understanding Layers

Layers are the foundation of non-destructive digital workflow. They let you work on parts of an image independently.

## Layer Basics
Think of layers as transparent sheets stacked on top of each other. Lower layers show through transparent areas of upper layers.

## Layer Types
- **Normal**: Standard paintable layer
- **Adjustment layer**: Non-destructive colour/value changes (Hue/Saturation, Curves, Levels)
- **Group/Folder**: Organises multiple layers
- **Clipping mask**: Clips layer content to the shape of the layer below

## Blend Modes
- **Multiply**: Darkens (good for shadows)
- **Screen**: Lightens (good for glow effects)
- **Overlay**: Adds contrast (good for colour grading)

## Layer Naming Best Practice
Always name your layers. Unnamed layers become impossible to manage on complex illustrations.

## Exercise
Create a simple illustration using at least 5 named layers: sketch, lineart, base colours, shadows, highlights.""",
            "beginner", "digital_art", 2, 40),

        _lesson("Digital Brushes and Mark-Making",
            """# Digital Brushes and Mark-Making

Digital brushes can simulate every traditional medium plus effects impossible in physical media.

## Brush Properties
- **Size**: Controlled by pen pressure (tip pressure) or manually
- **Opacity**: How transparent the stroke is (0% = invisible, 100% = solid)
- **Flow**: Rate of paint deposit per pass
- **Hardness**: Hard = crisp edges; Soft = feathered edges
- **Texture**: Adds paper or canvas grain

## Pressure Sensitivity
A good tablet has 4096 to 8192 pressure levels. Map pressure to both size and opacity for natural-feeling strokes.

## Creating Custom Brushes
In most software, define a brush by capturing a greyscale "stamp", setting spacing, and assigning scatter/rotation parameters.

## Exercise
Download 5 different community brush packs and test each one on a practice canvas. Note which you prefer for sketching, rendering, and texturing.""",
            "beginner", "digital_art", 3, 35),

        _lesson("Digital Sketching and Linework",
            """# Digital Sketching and Linework

Clean linework is a hallmark of professional digital illustration. It takes targeted practice.

## Sketching Workflow
1. Rough sketch (loose, low opacity, light colour)
2. Refined sketch (cleaner forms over the rough)
3. Clean linework (final lines on a new layer above sketches)

## Line Weight Variation
Vary your line weight (thicker at joints, thinner on straight runs) to add life and three-dimensionality.

## Stabilisation
Most digital tools offer stroke stabilisation that smooths imprecise hand movements. Use sparingly — over-stabilisation creates stiff, mechanical lines.

## Vector vs Raster
- **Raster lines**: Pixel-based; quality depends on resolution
- **Vector lines**: Math-based; infinitely scalable without loss

## Exercise
Trace over a reference photo of a hand using only clean, varied-weight lines. Focus on confident, deliberate strokes.""",
            "beginner", "digital_art", 4, 40),

        _lesson("Colour Blocking in Digital Art",
            """# Colour Blocking in Digital Art

Blocking in base colours efficiently is the fastest path from sketch to painted illustration.

## Flat Colour Method
1. Create a layer below your linework
2. Use the fill bucket or Lasso + Fill to block in large flat colour areas
3. Use separate layers per colour zone (skin, hair, clothing, background)

## Colour Selection Tips
- Start with mid-tones, not the darkest or lightest version of each colour
- Keep saturation moderate — you can always push it later

## Selection-Based Colouring
Lock the linework layer's transparency or use 'Select by colour' to isolate areas precisely before filling adjacent regions.

## Exercise
Take a sketch with clear distinct regions and fill every area with flat local colour in under 20 minutes.""",
            "beginner", "digital_art", 5, 35),

        _lesson("Digital Shading Techniques",
            """# Digital Shading Techniques

Shading transforms flat colour blocks into convincing three-dimensional forms.

## The Three-Value Method
1. Flat base colour
2. Shadow layer (Multiply blend mode, add darker shadow shapes)
3. Highlight layer (Screen or Add blend mode, add brightest spots)

## Cell Shading
Hard-edged shadow shapes with no gradients — inspired by animation cels and manga. Clean and graphic.

## Smooth Shading
Soft-edged brushes blended smoothly, simulating studio lighting. Used in hyperrealistic digital painting.

## Subsurface Scattering (Digital Simulation)
Warm reddish-orange glow around skin edges where light passes through the thin flesh (ears, fingertips). Add on a Glow or Screen layer with warm orange/red.

## Exercise
Shade the same sphere three ways: cell shading, smooth gradient shading, and rim-lit shading.""",
            "intermediate", "digital_art", 6, 50),

        _lesson("Texture and Detail Rendering",
            """# Texture and Detail Rendering

Adding convincing texture takes a digital illustration from flat to tangibly real.

## Photo Texture Overlays
Apply a photo of a real surface (fabric, wood, stone) as a layer in Overlay or Multiply mode at low opacity. The texture integrates naturally.

## Custom Texture Brushes
Brushes with grain simulate paper, canvas, charcoal, or watercolour texture in every stroke.

## Detail Hierarchy
Add the finest details last and only in the focal area. Peripheral areas should remain softer and less detailed.

## Noise and Grain
Add a light monochromatic noise layer (2–3% Gaussian noise) over the finished art in Overlay mode to unify and add visual richness.

## Exercise
Render a small detailed study of a piece of rough fabric, using at least one texture brush and one photo texture overlay.""",
            "intermediate", "digital_art", 7, 55),

        _lesson("Lighting Effects in Digital Art",
            """# Lighting Effects in Digital Art

Digital tools allow lighting effects that are difficult or impossible in traditional media.

## Adding Glow
Use a Screen, Add, or Linear Dodge blend mode layer. Paint soft spots of warm colour to imply glowing light sources.

## Rim Lighting
Paint a thin bright edge along the silhouette on a Screen layer. Works especially well for character illustration.

## Volumetric Light (Rays)
Create light beams with radial blur on a Screen layer, or use soft conical gradient brushes.

## Colour Grading
Add adjustment layers (Gradient Map, Colour Balance, Curves) above all other layers to unify the entire scene's lighting into a single coherent colour story.

## Exercise
Take a completed character illustration and add: (1) a warm point light on one side, (2) cool ambient on the other, (3) a single dramatic glow effect.""",
            "intermediate", "digital_art", 8, 55),

        _lesson("Digital Environment Design",
            """# Digital Environment Design

Creating convincing environments requires understanding of perspective, atmosphere, and lighting.

## Sketching the Environment
Block in sky, ground, and structural elements first. Keep the horizon line consistent with your composition goals.

## Atmospheric Perspective in Digital
Create separate layers for background, midground, and foreground. Desaturate and lighten background elements; keep foreground crisp and detailed.

## Value Composition for Environments
Establish a dominant value (light backgrounds, dark foreground) before adding colour. Test in greyscale.

## Workflow: Thumbnail to Final
1. Multiple tiny thumbnail sketches (exploring composition)
2. Select best, scale up
3. Block in large colour shapes
4. Add forms, lighting, and atmosphere
5. Detail only focal area

## Exercise
Design an exterior environment using the thumbnail-to-final workflow. Include sky, background, midground, and foreground.""",
            "intermediate", "digital_art", 9, 65),

        _lesson("Portfolio and Exporting Digital Art",
            """# Portfolio and Exporting Digital Art

Creating great work is only half the job — presenting it properly is equally important.

## Export Formats
- **PNG**: Lossless, supports transparency. For web and printing.
- **JPG**: Compressed; smaller file size but no transparency. For web display.
- **PSD/CSP**: Working files with layers intact. For archiving and editing.
- **PDF**: For print-ready designs and portfolios.
- **TIFF**: Lossless, large file size. Professional print standard.

## Resolution for Print vs Web
- Print: 300 dpi minimum at the final output size
- Web/screen: 72–96 dpi typical

## Portfolio Presentation
- Consistent framing and background across pieces
- Mockups: place illustration into photo mockups (books, phones, posters) to show real-world context
- Label every piece with title, medium, year

## Exercise
Export one piece in three formats (PNG, JPG, PDF) and compare file sizes and visual quality side by side.""",
            "advanced", "digital_art", 10, 45),
    ]


def digital_art_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "What hardware device is essential for comfortable digital painting and replaces mouse input?",
           ["A scanner", "A drawing tablet with pressure-sensitive stylus", "A second monitor", "A high-resolution printer"],
           "A drawing tablet with pressure-sensitive stylus",
           "A pressure-sensitive drawing tablet allows natural stroke control, size variation by pressure, and is far more ergonomic for prolonged digital painting."),
        _q(l[0]["id"], "Krita is notable among digital art software because:",
           ["It is exclusive to iPad", "It requires a subscription fee", "It is free and open-source", "It only supports vector drawing"],
           "It is free and open-source",
           "Krita is a professional-grade digital painting program available at no cost, making it highly accessible for beginners."),
        _q(l[0]["id"], "When creating a digital canvas for professional illustration, a recommended resolution is:",
           ["72 dpi at 500×500 px", "300 dpi at 2000×2000 px or larger", "150 dpi at any size", "96 dpi at 1920×1080 px"],
           "300 dpi at 2000×2000 px or larger",
           "300 dpi at sufficient pixel dimensions ensures the artwork will print at high quality and provides room for cropping."),
        _q(l[0]["id"], "Which software is particularly popular for illustration and manga creation?",
           ["Lightroom", "Clip Studio Paint", "Audacity", "DaVinci Resolve"],
           "Clip Studio Paint",
           "Clip Studio Paint is widely used by illustrators and manga artists for its specialised tools including perspective rulers, manga tones, and animation support."),
        _q(l[0]["id"], "Learning keyboard shortcuts in digital art software is important because:",
           ["They bypass the need for a drawing tablet", "They dramatically speed up workflow", "They improve brush quality automatically", "They are required to export files"],
           "They dramatically speed up workflow",
           "Keyboard shortcuts for common actions (undo, brush size, zoom, flip canvas) save enormous amounts of time in a professional context."),
    ]

    qs += [
        _q(l[1]["id"], "In digital art, what is the primary purpose of working with multiple layers?",
           ["To increase the file resolution", "To allow non-destructive editing of separate elements independently", "To automatically export different file formats", "To increase painting speed"],
           "To allow non-destructive editing of separate elements independently",
           "Layers let you modify, reorder, and delete individual elements without affecting the rest of the image."),
        _q(l[1]["id"], "The Multiply blend mode is most useful for:",
           ["Adding bright highlights and glow effects", "Adding shadows that darken underlying colours", "Creating transparent backgrounds", "Merging all layers into one"],
           "Adding shadows that darken underlying colours",
           "Multiply multiplies the pixel values, always resulting in a darker output, making it ideal for painting shadow layers over base colours."),
        _q(l[1]["id"], "A clipping mask layer in digital art:",
           ["Exports artwork as a masked region", "Clips its content to the shape of the layer directly below it", "Merges all selected layers", "Creates a selection from a colour range"],
           "Clips its content to the shape of the layer directly below it",
           "Clipping masks respect the transparency of the layer below; content only appears where the lower layer has pixels."),
        _q(l[1]["id"], "An adjustment layer (e.g. Hue/Saturation) modifies artwork:",
           ["Permanently on all layers", "Non-destructively, allowing changes to be reversed or edited at any time", "Only on the currently selected layer", "By flattening the image first"],
           "Non-destructively, allowing changes to be reversed or edited at any time",
           "Adjustment layers apply corrections to all layers below without permanently altering any pixels, enabling full reversibility."),
        _q(l[1]["id"], "The Screen blend mode is most useful for:",
           ["Deepening shadow areas", "Adding bright glow and lighting effects", "Creating seamless pattern repeats", "Removing colour from a layer"],
           "Adding bright glow and lighting effects",
           "Screen brightens the image by combining reversed pixel values — it never darkens, making it ideal for glowing light effects."),
    ]

    qs += [
        _q(l[2]["id"], "Brush opacity in digital painting controls:",
           ["The size of the brush stroke", "How transparent the stroke is (0% = invisible, 100% = fully opaque)", "The texture grain of the brush", "Whether the brush is pressure-sensitive"],
           "How transparent the stroke is (0% = invisible, 100% = fully opaque)",
           "Opacity governs transparency — a 50% opacity stroke allows the underlying layer to show through at 50%."),
        _q(l[2]["id"], "A hard brush in digital art produces:",
           ["Feathered, soft-edged strokes", "Crisp, well-defined edges", "Randomised scatter patterns", "Textured grain across the stroke"],
           "Crisp, well-defined edges",
           "Hardness controls edge definition; 100% hardness produces a solid-edged stroke with no feathering."),
        _q(l[2]["id"], "Pressure sensitivity on a drawing tablet is most useful for:",
           ["Automatically choosing colours", "Varying stroke size and opacity based on how hard you press the stylus", "Navigating the canvas by tilting the tablet", "Controlling layer visibility"],
           "Varying stroke size and opacity based on how hard you press the stylus",
           "Pressure sensitivity enables natural, expressive mark-making by varying size and opacity with pen pressure."),
        _q(l[2]["id"], "Flow in a digital brush differs from opacity because:",
           ["Flow has no effect on appearance", "Flow controls the rate of paint deposit per pass; multiple passes accumulate colour", "Flow permanently burns colour into the canvas", "Flow only works on greyscale brushes"],
           "Flow controls the rate of paint deposit per pass; multiple passes accumulate colour",
           "With low flow, a single stroke appears light; painting over the same area multiple times builds colour density up to the full opacity."),
        _q(l[2]["id"], "When creating a custom brush stamp, it should be created in:",
           ["Full colour (RGB)", "Greyscale (black defines opaque areas, white transparency)", "Monochromatic blue channel only", "CMYK for best print output"],
           "Greyscale (black defines opaque areas, white transparency)",
           "Brush stamps are greyscale images where black pixels paint fully and white pixels are transparent; grey tones produce partial opacity."),
    ]

    qs += [
        _q(l[3]["id"], "The correct order for creating clean digital linework is:",
           ["Linework → rough sketch → refined sketch", "Rough sketch → refined sketch → clean linework", "Colour blocking → linework → rough sketch", "Linework → colour blocking → sketch"],
           "Rough sketch → refined sketch → clean linework",
           "Starting loose and progressively refining is the universally practised digital sketching workflow."),
        _q(l[3]["id"], "Line weight variation in digital illustration means:",
           ["Using different colour values for each line", "Varying line thickness across the stroke to add depth and dynamism", "Changing the brush type every stroke", "Making all outline lines the same width"],
           "Varying line thickness across the stroke to add depth and dynamism",
           "Thicker lines at joints, corners, and near background elements and thinner lines on leading edges adds life and three-dimensionality to linework."),
        _q(l[3]["id"], "Stroke stabilisation in digital art tools:",
           ["Increases resolution automatically", "Smooths jerky hand movements to produce straighter, more controlled lines", "Replaces pressure sensitivity", "Converts raster lines to vector automatically"],
           "Smooths jerky hand movements to produce straighter, more controlled lines",
           "Stabilisation algorithms average stroke trajectory or introduce a slight delay, resulting in cleaner, smoother lines from imprecise hand movements."),
        _q(l[3]["id"], "Vector lines differ from raster lines in that:",
           ["Vector lines are made of pixels and lose quality when scaled", "Vector lines are math-based and scale infinitely without quality loss", "Vector lines can only be horizontal or vertical", "Raster lines support pressure sensitivity; vector cannot"],
           "Vector lines are math-based and scale infinitely without quality loss",
           "Vector graphics describe shapes mathematically (Bézier curves) and recalculate at any size, unlike raster's fixed pixel grid."),
        _q(l[3]["id"], "When practising clean linework, you should aim for:",
           ["Many short hesitant strokes joined together", "Slow, careful strokes with heavy stabilisation", "Confident, deliberate strokes drawn from the elbow and shoulder", "Strokes drawn by dragging with the mouse"],
           "Confident, deliberate strokes drawn from the elbow and shoulder",
           "Drawing from the elbow/shoulder rather than wrist produces longer, more controlled strokes — a fundamental skill for quality linework."),
    ]

    qs += [
        _q(l[4]["id"], "When blocking in flat colours, you should create the base colour layer:",
           ["Above the linework for easier painting", "Below the linework so lines remain visible on top", "Merged with the linework for efficiency", "On an adjustment layer"],
           "Below the linework so lines remain visible on top",
           "Placing the colour layer below the linework layer keeps the outlines crisp and visible over the filled colours."),
        _q(l[4]["id"], "Starting colour blocking with mid-tones rather than extremes is recommended because:",
           ["Mid-tones dry faster in digital art", "It gives flexibility to push both darker shadows and lighter highlights afterwards", "It automatically matches the colour scheme", "Mid-tones are easier to anti-alias"],
           "It gives flexibility to push both darker shadows and lighter highlights afterwards",
           "Beginning with mid-tones means you have room to go darker for shadows and lighter for highlights without immediately hitting the value extremes."),
        _q(l[4]["id"], "Locking a layer's transparency while colouring means:",
           ["No new pixels can be added outside existing filled areas", "The layer is protected from deletion", "Colours are sampled from below automatically", "Blending modes are disabled on that layer"],
           "No new pixels can be added outside existing filled areas",
           "Locking transparency prevents painting outside the current pixel footprint, making it easy to paint within shapes without spilling over edges."),
        _q(l[4]["id"], "Organising colours on separate layers (skin, hair, clothing) is best practice because:",
           ["File size is smaller with separate layers", "It enables independent editing of each colour zone without affecting others", "It automatically applies cell shading", "Colour layers can be stacked to create gradient effects"],
           "It enables independent editing of each colour zone without affecting others",
           "Separate colour layers preserve flexibility: you can adjust one colour region's hue, saturation, or value without disturbing the rest."),
        _q(l[4]["id"], "The primary goal of the colour blocking stage is to:",
           ["Render final detailed shading", "Establish all the local colour relationships across the image before shading", "Create the final linework", "Export the image for review"],
           "Establish all the local colour relationships across the image before shading",
           "Colour blocking establishes which colour goes where — it's a planning stage that makes subsequent shading and rendering much easier."),
    ]

    qs += [
        _q(l[5]["id"], "The Multiply blend mode is used in the digital shading workflow to:",
           ["Create bright highlights", "Add transparent shadow layers that darken the colours below", "Merge all colour layers", "Add a glow effect"],
           "Add transparent shadow layers that darken the colours below",
           "Painting on a Multiply layer adds darkening while preserving the hue and saturation of underlying colours, ideal for shadows."),
        _q(l[5]["id"], "Cell shading is characterised by:",
           ["Smooth, blended gradients across the form", "Hard-edged shadow shapes with no blending, inspired by animation", "Realistic subsurface scattering", "Volumetric atmospheric effects"],
           "Hard-edged shadow shapes with no blending, inspired by animation",
           "Cell shading uses flat, hard-edged shadow shapes typical of cel animation and graphic novel illustration."),
        _q(l[5]["id"], "Subsurface scattering simulation in digital skin shading adds:",
           ["Cold blue tones at skin edges", "Warm reddish-orange glow around thin skin areas where light penetrates", "Detailed pore texture", "Desaturated midtones only"],
           "Warm reddish-orange glow around thin skin areas where light penetrates",
           "Real skin allows warm light to scatter through thin areas like ears and fingertips, creating a glowing warm halo that painters simulate digitally."),
        _q(l[5]["id"], "The Screen blend mode is used in the shading workflow to:",
           ["Deepen shadow areas", "Paint bright highlights and specular reflections that lighten the image", "Desaturate mid-tones", "Add hard shadow edges"],
           "Paint bright highlights and specular reflections that lighten the image",
           "Screen only brightens; painting on a Screen layer adds light effects without the risk of pushing too dark."),
        _q(l[5]["id"], "In the three-value digital shading method, what is the correct order?",
           ["Shadow → highlights → base", "Highlights → base → shadow", "Base colour → shadow layer → highlight layer", "Linework → base → merge layers"],
           "Base colour → shadow layer → highlight layer",
           "Establishing the flat base first, then adding shadow depth, then highlight punch is the standard three-step digital shading workflow."),
    ]

    qs += [
        _q(l[6]["id"], "Applying a photo texture in Overlay blend mode at low opacity achieves:",
           ["Replacing all painted colours with the photo", "Subtly integrating the physical texture of the photo with the painted colours below", "Converting the painting to a photograph", "Removing detail from the focal area"],
           "Subtly integrating the physical texture of the photo with the painted colours below",
           "Overlay blends the texture's lights and darks into the painting, adding surface grain while preserving colour."),
        _q(l[6]["id"], "Where should the finest, most detailed texture work be placed in a composition?",
           ["Evenly across the entire image", "Only in the background to fill empty areas", "In the focal area; periphery should remain softer", "On the shadows only"],
           "In the focal area; periphery should remain softer",
           "Concentrated detail at the focal point draws the viewer's eye; leaving peripheral areas softer creates a natural focal hierarchy."),
        _q(l[6]["id"], "Adding a light Gaussian noise layer in Overlay mode at the end of painting is used to:",
           ["Reduce file size", "Unify the image and add visual richness", "Remove brush marks", "Convert the image to print resolution"],
           "Unify the image and add visual richness",
           "Light noise introduces subtle grain that ties together digital-looking smooth surfaces, giving the piece a more tangible, unified quality."),
        _q(l[6]["id"], "Custom texture brushes in digital art are used to:",
           ["Automatically paint at 300 dpi", "Simulate the appearance of real surface textures in every brushstroke", "Only work on the sketch layer", "Replace the need for all other brushes"],
           "Simulate the appearance of real surface textures in every brushstroke",
           "Texture brushes bake grain and surface properties into each mark, enabling quick, believable texture rendering."),
        _q(l[6]["id"], "Detail hierarchy in rendering means:",
           ["Every area should have equal levels of detail", "Fine details are only added last and concentrated in the focal zone", "Background details should always be sharper than foreground", "Detail is added in a single pass from top to bottom"],
           "Fine details are only added last and concentrated in the focal zone",
           "Working from large shapes to small details, with the most detail concentrated in the focal area, creates natural visual hierarchy."),
    ]

    qs += [
        _q(l[7]["id"], "The Linear Dodge (Add) blend mode in digital lighting is used to:",
           ["Darken areas around a light source", "Create very bright, high-intensity glow and light effects", "Desaturate a light source colour", "Invert the colours beneath the layer"],
           "Create very bright, high-intensity glow and light effects",
           "Linear Dodge adds layer pixel values directly, producing a very bright result ideal for intense light sources and glows."),
        _q(l[7]["id"], "Rim lighting in character illustration is added on a Screen layer to:",
           ["Create a soft glow around the figure's core", "Paint a bright edge along the character's silhouette separating it from the background", "Add ambient occlusion to shadows", "Soften any harsh shadow edges"],
           "Paint a bright edge along the character's silhouette separating it from the background",
           "Rim light (back light) picks out the silhouette edge, making the character 'pop' off the background."),
        _q(l[7]["id"], "Colour grading using adjustment layers at the top of a layer stack:",
           ["Only affects the layer directly below", "Unifies the entire scene's colour and lighting with a single non-destructive pass", "Permanently changes all embedded layer colours", "Reduces the painting's resolution"],
           "Unifies the entire scene's colour and lighting with a single non-destructive pass",
           "Placing colour correction and grading adjustment layers at the stack's top applies the same treatment to the full composite, creating a unified look."),
        _q(l[7]["id"], "Volumetric light rays (god rays) in digital art are typically achieved using:",
           ["A hard flat brush on a Normal layer", "Radial blur on a light-coloured shape layer set to Screen", "Multiply shadows in the shadow areas", "Painting each ray individually on a separate layer"],
           "Radial blur on a light-coloured shape layer set to Screen",
           "A bright soft shape radially blurred from the light source origin, set to Screen, creates convincing volumetric light shafts."),
        _q(l[7]["id"], "To convey warm and cool light contrast in a digital scene, the approach is to:",
           ["Use only Hue/Saturation adjustments", "Paint warm tones on the lit side and cool tones on the shadow side on separate layers", "Desaturate all shadow pixels", "Apply a single colour wash over the whole composition"],
           "Paint warm tones on the lit side and cool tones on the shadow side on separate layers",
           "Separate layers for warm and cool lighting allow full control over temperature contrast, one of the most powerful tools for creating convincing light."),
    ]

    qs += [
        _q(l[8]["id"], "In a digital environment painting workflow, thumbnailing refers to:",
           ["Creating the final high-resolution canvas", "Making many small rapid composition sketches before committing to a direction", "Exporting reduced-size preview files", "Sketching only the foreground elements"],
           "Making many small rapid composition sketches before committing to a direction",
           "Tiny thumbnail sketches are fast to create and let you compare many compositional ideas before investing time in the full piece."),
        _q(l[8]["id"], "Atmospheric perspective in a digital environment is best achieved by:",
           ["Making all elements in the scene and background equally detailed", "Desaturating and lightening background layers while keeping foreground crisp and detailed", "Darkening the background and lightening the foreground", "Using only one layer for the entire environment"],
           "Desaturating and lightening background layers while keeping foreground crisp and detailed",
           "Aerial perspective physically increases the amount of atmosphere between viewer and distant objects, washing them out and softening their edges."),
        _q(l[8]["id"], "A common value dominance strategy for outdoor environments is:",
           ["Equal 50/50 light and dark areas", "Light, value-washed sky / darker, richer foreground elements", "Dark sky with fully black foreground", "Identical value across all depth layers"],
           "Light, value-washed sky / darker, richer foreground elements",
           "Light sky against darker, richer ground elements creates instant depth and a natural visual anchor for the composition."),
        _q(l[8]["id"], "Why should an environment painting be tested in greyscale during the workflow?",
           ["Greyscale export is required for printing", "To confirm that the value structure reads clearly before colour is introduced", "To reduce the file size", "Greyscale view checks for brush texture quality"],
           "To confirm that the value structure reads clearly before colour is introduced",
           "Checking in greyscale reveals if the large value shapes create a readable image independent of colour — a sign of a strong compositional foundation."),
        _q(l[8]["id"], "Separating an environment into background, midground, and foreground layers allows:",
           ["Automatic application of aerial perspective to all layers", "Independent editing of each spatial zone, enabling easy depth adjustments", "Merging at export for the final flat file", "Colour grading that affects only the foreground"],
           "Independent editing of each spatial zone, enabling easy depth adjustments",
           "Separate spatial layers let you push saturation, sharpness, and value independently in each plane — for precise control over depth."),
    ]

    qs += [
        _q(l[9]["id"], "PNG is the preferred export format when you need:",
           ["The smallest possible file size", "Lossy compression for web streaming", "Lossless quality with transparency support", "Print-ready CMYK colour space"],
           "Lossless quality with transparency support",
           "PNG provides lossless compression and supports an alpha (transparency) channel — ideal for web assets and print-ready images."),
        _q(l[9]["id"], "What resolution is the minimum standard for professional print output?",
           ["72 dpi", "150 dpi", "300 dpi", "600 dpi"],
           "300 dpi",
           "300 dpi (dots per inch) is the widely accepted minimum for commercial printing with no visible pixel artifacts at normal viewing distances."),
        _q(l[9]["id"], "JPG differs from PNG primarily because:",
           ["JPG supports transparency; PNG does not", "JPG uses lossy compression and does not support transparency; PNG is lossless", "JPG is for print; PNG is for web only", "JPG stores layer information; PNG does not"],
           "JPG uses lossy compression and does not support transparency; PNG is lossless",
           "JPG achieves small file sizes through lossy compression that discards colour information, and has no transparency channel."),
        _q(l[9]["id"], "A working file (PSD or CSP) should be kept because:",
           ["It has smaller file size than PNG", "It retains all layers and editing data for future revisions", "It is the only format accepted by print services", "It automatically converts to 300 dpi"],
           "It retains all layers and editing data for future revisions",
           "Working files preserve the full layer structure and settings, allowing complete re-editing at any point — unlike flattened export formats."),
        _q(l[9]["id"], "When building a portfolio, using mockups (placing art in photo mockups of books or posters) helps to:",
           ["Reduce the digital file size", "Demonstrate how the work looks in real-world context", "Convert resolution to print standard", "Remove the need for proper framing"],
           "Demonstrate how the work looks in real-world context",
           "Mockups situate the work in a relatable context (a phone screen, a book cover, a poster) helping clients and viewers understand the work's practical application."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 5 — Design  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def design_lessons():
    return [
        _lesson("Principles of Design",
            """# Principles of Design

The principles of design are the foundational guidelines used to arrange visual elements into effective, communicative compositions.

## The Seven Principles
1. **Balance**: Equal visual weight — symmetrical (formal) or asymmetrical (dynamic)
2. **Contrast**: Difference in value, colour, size, or shape that creates visual interest
3. **Emphasis**: The focal point — what the viewer should notice first
4. **Movement**: The path the viewer's eye follows through the composition
5. **Pattern**: Repetition of elements creating visual rhythm
6. **Unity**: How well all elements belong together
7. **Proportion**: Size relationships between elements

## Exercise
Analyse three professional logo designs. Identify which design principles are most prominent in each and explain how they contribute to the logo's effectiveness.""",
            "beginner", "design", 1, 35),

        _lesson("The Elements of Design",
            """# The Elements of Design

The elements of design are the raw building blocks used in any visual composition.

## The Seven Elements
1. **Line**: Defines edges, implies movement, guides the eye
2. **Shape**: 2D flat areas — geometric or organic
3. **Form**: 3D objects or the illusion of them
4. **Space**: Positive (occupied) and negative (empty) areas
5. **Texture**: How a surface looks or would feel
6. **Value**: Lightness and darkness
7. **Colour**: Hue, saturation, and value combined

## Negative Space
Empty space around and between subjects is as important as the subjects themselves. It creates breathing room and can reinforce meaning.

## Exercise
Create a simple composition using only abstract geometric shapes that demonstrates at least four of the seven elements.""",
            "beginner", "design", 2, 35),

        _lesson("Typography Fundamentals",
            """# Typography Fundamentals

Typography is the art of arranging type to make language visible and effective.

## Typeface Categories
- **Serif**: Has small strokes (serifs) at the ends of letterforms. Traditional, readable in print. (Times New Roman)
- **Sans-serif**: Clean, no serifs. Modern, clear at all sizes. (Helvetica, Arial)
- **Script**: Mimics handwriting. Decorative use only.
- **Display**: Decorative typefaces for headlines only

## Key Typography Terms
- **Kerning**: Space between individual letter pairs
- **Leading**: Space between lines of text
- **Tracking**: Uniform spacing across a range of letters
- **Hierarchy**: Using different sizes and weights to signal importance

## Readability vs Legibility
Legibility = can you distinguish individual letters? Readability = is running text easy to read over longer passages?

## Exercise
Design a simple event poster using exactly two typefaces: one serif for the headline, one sans-serif for body text.""",
            "beginner", "design", 3, 40),

        _lesson("Layout and Grid Systems",
            """# Layout and Grid Systems

Grids impose invisible structure that makes layouts clear, consistent, and professional.

## Why Grids?
- Create alignment and consistency
- Establish rhythm and predictability
- Speed up layout decisions

## Common Grid Types
- **Manuscript grid**: Single large column. Used in books and long-form text.
- **Column grid**: 2–12 columns. Used in magazines and web layouts.
- **Modular grid**: Rows and columns intersecting. Used in complex editorial design.
- **Baseline grid**: Horizontal lines spaced at leading intervals aligning body text.

## Rule of Thirds
Divide the canvas into a 3×3 grid. Place key elements at the four intersection points for natural visual balance.

## Whitespace
Empty areas aren't wasted space — they're breathing room that increases comprehension and visual quality.

## Exercise
Redesign a simple webpage layout using a 12-column grid. Snap all elements to grid columns and margins.""",
            "beginner", "design", 4, 45),

        _lesson("Colour in Graphic Design",
            """# Colour in Graphic Design

Colour is the most immediate, emotional element in graphic design.

## Brand Colour Systems
Major brands select a primary, secondary, and neutral colour palette used consistently across all touchpoints.

## Accessible Colour
WCAG (Web Content Accessibility Guidelines) require a minimum contrast ratio of 4.5:1 between text and background colour for standard text readability.

## Colour Modes
- **RGB**: Use for screens and digital output
- **CMYK**: Use for print output
- **Pantone (PMS)**: Standardised spot colours for exact, reproducible brand colours in print

## 60/30/10 Rule
A common design formula: 60% dominant colour, 30% secondary colour, 10% accent colour. Creates balance without monotony.

## Exercise
Create a simple brand identity (logo + 3 colour palette) for an imaginary coffee shop. Justify each colour choice.""",
            "beginner", "design", 5, 40),

        _lesson("Visual Hierarchy",
            """# Visual Hierarchy

Visual hierarchy determines the order in which a viewer's eye notices elements. Intentional hierarchy communicates importance.

## Creating Hierarchy
- **Size**: Larger elements attract attention first
- **Colour**: High contrast or saturated colour draws the eye
- **Weight**: Bold text reads before regular weight
- **Position**: Top-left and top-centre are primary reading zones (in Western culture)
- **Whitespace**: Isolating an element gives it importance

## F-Pattern and Z-Pattern
Research shows web readers scan in an F-pattern (two horizontal passes then vertically down the left). Print readers often follow a Z-pattern across the top, diagonally, then across the bottom.

## Three-Level Hierarchy
Structure most designs with three hierarchy levels: primary (most important), secondary (supporting), tertiary (supplementary).

## Exercise
Take a poorly designed flyer (dense, equal emphasis everywhere) and redesign it with clear three-level hierarchy.""",
            "intermediate", "design", 6, 50),

        _lesson("Logo Design",
            """# Logo Design

A logo is the most distilled, essential mark of a brand's identity. It must work in any context.

## Types of Logos
- **Wordmark**: Only the brand name in a distinctive typeface (Coca-Cola)
- **Lettermark**: Initials only (IBM)
- **Pictorial mark**: Abstract or literal icon (Apple)
- **Combination mark**: Icon + wordmark together (Nike + name)
- **Emblem**: Text enclosed within a shape (Starbucks)

## Logo Requirements
- Must work in black and white (no colour dependency)
- Must scale from a smartphone favicon to a billboard
- Must be immediately recognisable and distinctive

## Simplicity Principle
Add nothing that doesn't contribute to the concept. Complexity doesn't communicate — simplicity does.

## Exercise
Design three logo concepts for the same imaginary brand using three different logo types. Test each in black and white.""",
            "intermediate", "design", 7, 55),

        _lesson("User Interface Design Basics",
            """# User Interface Design Basics

UI design creates the visual layer of digital products — the buttons, forms, icons, and screens people interact with.

## UI Design Components
- **Buttons**: Primary, secondary, and destructive button hierarchy
- **Forms**: Labels above fields. Placeholder text ≠ label.
- **Navigation**: Clear, consistent, accessible
- **Icons**: Universally understood or labelled

## Design System / Component Library
A collection of reusable UI components with consistent styling. Ensures visual consistency across a product.

## States
Every interactive element needs: default, hover, focus, active, disabled, and error states.

## 8-Point Grid
Base all sizing and spacing decisions on multiples of 8px (8, 16, 24, 32, 48, 64). Produces harmonious, consistent layouts.

## Exercise
Design a mobile login screen (email/password/button) following the 8-point grid. Include all interactive states for the button.""",
            "intermediate", "design", 8, 55),

        _lesson("Design for Print",
            """# Design for Print

Print design has technical requirements that differ significantly from screen design.

## Key Specifications
- **Resolution**: 300 dpi minimum at final output size
- **Colour mode**: CMYK (not RGB)
- **Bleed**: 3mm of extra design beyond the trim line, preventing white edges after cutting
- **Safe zone**: Keep critical content 5mm inside the trim edge

## File Formats for Print
- **PDF/X**: Industry-standard print-ready format
- **AI / EPS**: Vector format for logos and print-ready artwork
- **TIFF**: High-quality raster for photos in layouts

## Paper Weight
- 80–90 gsm: standard office paper
- 115–170 gsm: flyers and brochures
- 250–400 gsm: business cards and covers

## Exercise
Set up an A5 flyer in your design software with correct bleed, safe zone, CMYK colour mode, and 300 dpi resolution.""",
            "intermediate", "design", 9, 50),

        _lesson("Brand Identity Design",
            """# Brand Identity Design

A brand identity system is the comprehensive visual language that represents an organisation across all communication.

## Components of a Brand Identity
- **Logo** (all variations)
- **Colour palette** (primary, secondary, neutral)
- **Typography** (headline, body, display typefaces)
- **Imagery style** (photography direction, illustration style)
- **Iconography**
- **Voice and tone** (written personality)

## Brand Guidelines Document
A PDF that documents every element — how to use the logo (including misuse examples), which typefaces and where, the exact colour codes (HEX, RGB, CMYK, Pantone).

## Brand Consistency
Every touchpoint (website, business card, social post, packaging) must feel like it comes from the same source. Inconsistency erodes trust.

## Exercise
Create a one-page brand guideline sheet for your imaginary coffee shop: include logo, colour swatches (with codes), and typography specifications.""",
            "advanced", "design", 10, 70),
    ]


def design_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "Which design principle describes the focal point that viewers notice first?",
           ["Balance", "Pattern", "Emphasis", "Unity"],
           "Emphasis",
           "Emphasis is the design principle that creates a clear focal point, directing the viewer's attention to the most important element first."),
        _q(l[0]["id"], "Asymmetrical balance in design is considered:",
           ["More formal and rigid than symmetrical balance", "Less interesting than symmetrical balance", "Dynamic and visually engaging", "The lack of any visual organisation"],
           "Dynamic and visually engaging",
           "Asymmetrical balance achieves visual equilibrium through contrast rather than mirror symmetry, creating more dynamic, interesting compositions."),
        _q(l[0]["id"], "The principle of contrast in design is created by:",
           ["Using identical sizes and colours throughout", "Creating difference in value, colour, size, or shape", "Repeating elements across the composition", "Placing all elements at equal distances"],
           "Creating difference in value, colour, size, or shape",
           "Contrast is produced whenever two unlike elements are placed together — it creates visual interest and separates information."),
        _q(l[0]["id"], "Unity in a design refers to:",
           ["Making every element the same size", "How well all elements belong together as a coherent whole", "Using only one colour throughout", "Centering every element on the canvas"],
           "How well all elements belong together as a coherent whole",
           "Unity is achieved when all elements share characteristics (style, colour, spacing) that make them feel part of the same composition."),
        _q(l[0]["id"], "The principle of movement in design refers to:",
           ["Literal animation or motion graphics", "The path along which a viewer's eye naturally travels through the composition", "The physical motion required to scroll the design", "Diagonal lines only"],
           "The path along which a viewer's eye naturally travels through the composition",
           "Implied movement is created by line direction, scale change, and compositional flow that guides the viewer through the design in a intended sequence."),
    ]

    qs += [
        _q(l[1]["id"], "Negative space in design refers to:",
           ["Dark or black areas in a composition", "Empty space around and between subjects", "Areas reserved for body text", "The background colour only"],
           "Empty space around and between subjects",
           "Negative (or white) space is the empty area surrounding and between subjects; it is an active design element that creates clarity and breathing room."),
        _q(l[1]["id"], "Which of these is a shape rather than a form?",
           ["A sculpted sphere", "A drawn circle on a flat canvas", "A 3D rendered cube", "A cast shadow creating volume"],
           "A drawn circle on a flat canvas",
           "Shapes are flat, 2D areas. A drawn circle has no depth; a 3D rendered sphere or sculpted object would be a form."),
        _q(l[1]["id"], "Line in design can be used to:",
           ["Only outline shapes", "Define edges, create movement, and guide the viewer's eye", "Only separate columns of text", "Indicate scale only"],
           "Define edges, create movement, and guide the viewer's eye",
           "Lines serve multiple functions: they define shapes, imply direction and movement, and act as leading lines directing viewer attention."),
        _q(l[1]["id"], "Positive space in a design composition is:",
           ["The empty area surrounding subjects", "The space occupied by the main subjects and elements", "Any white or light area", "The area between columns in a grid"],
           "The space occupied by the main subjects and elements",
           "Positive space is where the subjects exist; negative space is everywhere else. Both are equally important design considerations."),
        _q(l[1]["id"], "Texture in graphic design can be:",
           ["Only physical (felt by touch)", "Either physical on print pieces or visual (simulated through imagery)", "Only applied through filters in software", "Created only with brush tools"],
           "Either physical on print pieces or visual (simulated through imagery)",
           "Texture can be physical (embossed, spot UV on print) or visual (photographic or illustrated texture that implies surface quality)."),
    ]

    qs += [
        _q(l[2]["id"], "Kerning in typography refers to:",
           ["The space between lines of text", "The space between individual letter pairs", "The overall weight of the typeface", "The size of the typeface in points"],
           "The space between individual letter pairs",
           "Kerning adjusts the space between specific pairs of letters to achieve optically even spacing throughout a word."),
        _q(l[2]["id"], "A serif typeface differs from a sans-serif typeface because:",
           ["Serif typefaces have only capital letters", "Serif typefaces have small decorative strokes at the ends of letterforms", "Serif typefaces are always bolder", "Serif typefaces cannot be used digitally"],
           "Serif typefaces have small decorative strokes at the ends of letterforms",
           "Serifs are the small horizontal strokes at the base of letters; sans-serif means 'without serifs'."),
        _q(l[2]["id"], "Leading in typography controls:",
           ["Space between individual characters", "Space between lines of text", "The x-height of characters", "The weight of a typeface"],
           "Space between lines of text",
           "Leading (rhymes with 'bedding') is the vertical space between baselines of successive lines of text."),
        _q(l[2]["id"], "Using more than two typefaces in a single design is generally:",
           ["Always encouraged for variety", "Best avoided unless there is a clear strategic reason", "Required for professional work", "Restricted to headline text only"],
           "Best avoided unless there is a clear strategic reason",
           "Two typefaces (one serif + one sans-serif, or similar) are usually sufficient; more typefaces create visual noise and incoherence."),
        _q(l[2]["id"], "Typographic hierarchy is created through:",
           ["Using only one typeface size", "Varying sizes, weights, and spacing to signal the relative importance of each text element", "Placing all type in the vertical centre", "Using only display typefaces throughout"],
           "Varying sizes, weights, and spacing to signal the relative importance of each text element",
           "Hierarchy guides the reader through the information in the intended priority order using visual differentiation."),
    ]

    qs += [
        _q(l[3]["id"], "The primary purpose of a design grid is to:",
           ["Force all elements into a rigid symmetrical layout", "Impose invisible structure creating alignment, consistency, and rhythm", "Replace the need for whitespace", "Determine colour relationships"],
           "Impose invisible structure creating alignment, consistency, and rhythm",
           "Grids are invisible organisational frameworks that help designers place elements in harmonious, consistent, readable arrangements."),
        _q(l[3]["id"], "A 12-column grid is most commonly used for:",
           ["Single-column book typesetting", "Web and magazine layouts requiring flexible column combinations", "Logo design", "Wayfinding and signage systems"],
           "Web and magazine layouts requiring flexible column combinations",
           "12 columns divide evenly into 2, 3, 4, and 6 equal sections, offering maximum flexibility for responsive web and editorial layouts."),
        _q(l[3]["id"], "Whitespace in design is best described as:",
           ["Wasted space that should be filled with content", "Empty areas that provide breathing room, improve comprehension, and signal quality", "Only the white paper visible before printing", "Space reserved for a future version of the design"],
           "Empty areas that provide breathing room, improve comprehension, and signal quality",
           "Intentional whitespace reduces cognitive load, improves readability, and is a hallmark of high-quality, confidence-in-simplicity design."),
        _q(l[3]["id"], "The Rule of Thirds divides the canvas into:",
           ["Three equal horizontal bands", "A 3×3 grid with nine equal sections", "Four quadrants", "A central circle and surrounding ring"],
           "A 3×3 grid with nine equal sections",
           "The Rule of Thirds creates a 3×3 grid; placing key elements at the four intersection points creates naturally balanced, dynamic compositions."),
        _q(l[3]["id"], "A baseline grid in typography is used to:",
           ["Create equal margins on all sides", "Align text to consistent horizontal intervals for vertical rhythm", "Set the font size for body copy", "Determine column width"],
           "Align text to consistent horizontal intervals for vertical rhythm",
           "A baseline grid ensures all text lines sit on consistent horizontal intervals, creating comfortable vertical rhythm across the layout."),
    ]

    qs += [
        _q(l[4]["id"], "Pantone (PMS) colours are used in professional print design because:",
           ["They are free to use commercially", "They are standardised spot colours ensuring exact colour consistency across print runs", "They are brighter than RGB colours", "They automatically convert to CMYK"],
           "They are standardised spot colours ensuring exact colour consistency across print runs",
           "Pantone's standardised ink mixing system ensures the same colour appears identically regardless of which printer or press produces it."),
        _q(l[4]["id"], "The WCAG minimum contrast ratio for standard body text against its background is:",
           ["2:1", "3:1", "4.5:1", "7:1"],
           "4.5:1",
           "WCAG level AA requires a minimum 4.5:1 contrast ratio for standard text to ensure readability for users with low vision."),
        _q(l[4]["id"], "The 60/30/10 colour rule in design refers to:",
           ["60% primary colour, 30% secondary colour, 10% accent colour", "60% white, 30% colour, 10% black", "60% warm, 30% cool, 10% neutral", "60% typography, 30% imagery, 10% colour"],
           "60% primary colour, 30% secondary colour, 10% accent colour",
           "The 60/30/10 rule creates a balanced, harmonious colour distribution that avoids monotony and visual chaos."),
        _q(l[4]["id"], "RGB colour mode should be used when designing for:",
           ["Printed brochures and books", "Screens and digital output only", "Pantone-matched brand colours", "Large-format vinyl signage"],
           "Screens and digital output only",
           "RGB is the native colour model for screens; print requires CMYK conversion to ensure accurate ink colour reproduction."),
        _q(l[4]["id"], "In brand colour systems, choosing a primary, secondary, and neutral palette helps:",
           ["Reduce the need for photography", "Create consistent, recognisable visual identity across all brand touchpoints", "Ensure the brand works only in print", "Limit the number of typefaces that can be used"],
           "Create consistent, recognisable visual identity across all brand touchpoints",
           "A defined colour palette ensures that all brand materials feel cohesive and instantly recognisable as belonging to the same brand."),
    ]

    qs += [
        _q(l[5]["id"], "In Western reading culture, which area of a layout is typically the primary reading zone?",
           ["Bottom-right", "Top-left and top-centre", "Centre of the composition", "Bottom-left only"],
           "Top-left and top-centre",
           "In cultures that read left to right, the eye naturally enters at the top-left — making it the most prominent position for primary content."),
        _q(l[5]["id"], "Creating visual hierarchy with size means:",
           ["Making all elements smaller to appear minimal", "Making more important elements larger to draw attention first", "Using only two different sizes throughout the design", "Scaling all type to 12pt for consistency"],
           "Making more important elements larger to draw attention first",
           "Size is one of the strongest cues for visual priority — larger elements are noticed before smaller ones."),
        _q(l[5]["id"], "The F-pattern in web reading behaviour describes:",
           ["A wave-like reading path from bottom to top", "Two horizontal passes near the top then a vertical scan down the left margin", "A diagonal reading path from top-left to bottom-right", "Circular eye movement from the centre outward"],
           "Two horizontal passes near the top then a vertical scan down the left margin",
           "Eye-tracking research (Nielsen Norman Group) shows most web readers scan in an F-pattern, informing where the most important content should be placed."),
        _q(l[5]["id"], "Isolating an element with whitespace around it increases its:",
           ["Negative visual weight", "Perceived importance and visual prominence", "Legibility only at small sizes", "Contrast with the background"],
           "Perceived importance and visual prominence",
           "An element with generous whitespace around it stands apart and signals high importance to the viewer."),
        _q(l[5]["id"], "A three-level hierarchy in a design typically consists of:",
           ["Title, subtitle, caption", "Primary, secondary, and tertiary elements of information", "Colour, form, and line", "Background, midground, foreground"],
           "Primary, secondary, and tertiary elements of information",
           "Three levels of hierarchy give structure without complexity: primary (most important), secondary (supporting info), tertiary (supplementary detail)."),
    ]

    qs += [
        _q(l[6]["id"], "A wordmark logo is:",
           ["An abstract symbol or icon only", "The brand name set in a distinctive typeface with no accompanying symbol", "Text enclosed inside a shape", "Initials only without the full name"],
           "The brand name set in a distinctive typeface with no accompanying symbol",
           "A wordmark uses only the company name in a carefully chosen or custom typeface (e.g. Google, Coca-Cola)."),
        _q(l[6]["id"], "Why must a logo work in black and white?",
           ["Most clients print in black and white", "It cannot rely on colour alone to communicate — it must work in all reproduction contexts", "Colour logos are not accepted by trademark offices", "Black and white is always the primary brand colour"],
           "It cannot rely on colour alone to communicate — it must work in all reproduction contexts",
           "A logo that only works in colour will fail when faxed, embossed, or reproduced in single-colour contexts."),
        _q(l[6]["id"], "The simplicity principle in logo design states:",
           ["Logos should use many fine details for richness", "Add nothing that does not contribute to the concept — complexity hinders communication", "Simple logos are only suitable for small businesses", "A logo must contain at least three design elements"],
           "Add nothing that does not contribute to the concept — complexity hinders communication",
           "The most memorable, durable logos (Apple, Nike, Target) are simple. Simplicity allows instant recognition at any size."),
        _q(l[6]["id"], "A combination mark logo combines:",
           ["Two different fonts", "An icon/symbol and the brand wordmark together", "A lettermark with an abstract shape", "A photograph and a typographic identity"],
           "An icon/symbol and the brand wordmark together",
           "Combination marks pair a pictorial icon with the brand name text, allowing both to be used independently or together."),
        _q(l[6]["id"], "The Nike logo (swoosh alone, without text) is an example of:",
           ["An emblem", "A wordmark", "A pictorial (symbol) mark used independently", "A lettermark"],
           "A pictorial (symbol) mark used independently",
           "The Nike swoosh is an abstract pictorial mark so recognisable that it can be used without the 'Nike' wordmark."),
    ]

    qs += [
        _q(l[7]["id"], "The 8-point grid system in UI design means:",
           ["All text must be 8pt", "All sizing and spacing values are multiples of 8 (8, 16, 24, 32...)", "Grids have 8 columns only", "Buttons are always 8px tall"],
           "All sizing and spacing values are multiples of 8 (8, 16, 24, 32...)",
           "Basing all layout decisions on multiples of 8 creates natural proportion and consistency across the entire UI."),
        _q(l[7]["id"], "Using placeholder text as a form field label is considered poor practice because:",
           ["Placeholder text increases file size", "It disappears when the user starts typing, removing the label at the moment it's most needed", "It reduces contrast ratio", "It cannot be styled with CSS"],
           "It disappears when the user starts typing, removing the label at the moment it's most needed",
           "Labels must persist above or beside input fields; if placeholder text replaces them, users lose context once they begin typing."),
        _q(l[7]["id"], "A design system / component library is valuable because:",
           ["It reduces the number of designers needed", "It ensures visual consistency and speeds production by providing reusable components", "It replaces the need for user testing", "It is only useful for very large teams"],
           "It ensures visual consistency and speeds production by providing reusable components",
           "A design system codifies decisions once; every designer/developer uses the same pre-built components, preventing inconsistency."),
        _q(l[7]["id"], "Which button states must be designed for complete interactive coverage?",
           ["Default only", "Default and hover only", "Default, hover, focus, active, disabled, and error", "Default, active, and error only"],
           "Default, hover, focus, active, disabled, and error",
           "Interactive elements must communicate all states clearly to users — including accessibility states like focus (keyboard navigation) and disabled."),
        _q(l[7]["id"], "In UI design, which element represents a destructive action (e.g. deleting data)?",
           ["A green primary button", "A subtle text link", "A red or strongly differentiated button", "A blue outlined secondary button"],
           "A red or strongly differentiated button",
           "Destructive buttons (delete, remove, cancel account) are typically styled in red or with a distinct UI treatment to warn users before irreversible actions."),
    ]

    qs += [
        _q(l[8]["id"], "Bleed in print design refers to:",
           ["Ink bleeding through to the back of the paper", "Extra design area beyond the trim line to prevent white edges after cutting", "The minimum margin inside the safe zone", "Over-saturated ink colour"],
           "Extra design area beyond the trim line to prevent white edges after cutting",
           "After cutting, paper shifts slightly; bleed (typically 3mm) ensures that background colour extends to the very edge without white gaps."),
        _q(l[8]["id"], "The safe zone in print design is:",
           ["The same as the bleed area", "The area well inside the trim line where critical content must be kept to avoid accidental cropping", "The area reserved for copyright notices", "The maximum printable area defined by the printer"],
           "The area well inside the trim line where critical content must be kept to avoid accidental cropping",
           "The safe zone (typically 5mm inside trim) ensures logos, text, and key elements are never trimmed during the cutting process."),
        _q(l[8]["id"], "What colour mode must be used when preparing files for professional print?",
           ["RGB", "LAB", "HSB", "CMYK"],
           "CMYK",
           "Print presses use Cyan, Magenta, Yellow, and Key (Black) inks — CMYK. Submitting RGB files causes unpredictable colour shifts when converted."),
        _q(l[8]["id"], "The PDF/X format is used in print production because:",
           ["It is the smallest file format for email", "It is a standardised, print-industry format that embeds all fonts and colour profiles", "It supports multiple pages only", "It automatically converts to the correct dpi"],
           "It is a standardised, print-industry format that embeds all fonts and colour profiles",
           "PDF/X (ISO standard) ensures the file is fully self-contained with embedded fonts, images, and ICC colour profiles — preventing output errors."),
        _q(l[8]["id"], "Minimum paper weight for business cards is typically:",
           ["80 gsm", "115 gsm", "250 gsm", "400 gsm"],
           "250 gsm",
           "Business cards require a sturdy, premium feel; 250–400 gsm is typical, compared to 80 gsm standard office paper."),
    ]

    qs += [
        _q(l[9]["id"], "A brand guidelines document serves the purpose of:",
           ["Listing the company's financial information", "Documenting how all visual brand elements should be used consistently", "Replacing the need for a logo", "Specifying only the typography rules"],
           "Documenting how all visual brand elements should be used consistently",
           "Brand guidelines ensure every designer, agency, or vendor reproduces the brand correctly no matter where or when they work with it."),
        _q(l[9]["id"], "Which of the following is NOT typically part of a full brand identity system?",
           ["Logo variations", "Typography specification", "Colour palette with colour codes", "The company's staff payroll"],
           "The company's staff payroll",
           "A brand identity system covers visual and communication elements; payroll is a business administration document unrelated to brand identity."),
        _q(l[9]["id"], "Brand consistency across touchpoints is important because:",
           ["It reduces the cost of logo design", "Inconsistency confuses customers and erodes trust over time", "It allows fewer touchpoints to be designed", "It eliminates the need for brand guidelines"],
           "Inconsistency confuses customers and erodes trust over time",
           "Every touchpoint is an opportunity to reinforce or weaken recognition; inconsistency signals a lack of professionalism and dilutes brand equity."),
        _q(l[9]["id"], "In brand identity, specifying HEX, RGB, CMYK, and Pantone values for each colour ensures:",
           ["The logo can only be reproduced digitally", "Colours reproduce consistently across both screen and print production", "Typography is matched to the colour scheme", "The brand works only in print"],
           "Colours reproduce consistently across both screen and print production",
           "Each colour model is used in a different context; specifying all values ensures the same colour can be accurately reproduced regardless of medium."),
        _q(l[9]["id"], "Logo misuse examples in brand guidelines are included to:",
           ["Provide alternative logo versions", "Show designers and vendors what they must never do to the logo", "Allow creative freedom around the logo", "Display the logo's historical variations"],
           "Show designers and vendors what they must never do to the logo",
           "Misuse examples proactively prevent common mistakes such as stretching, recolouring, or placing the logo on clashing backgrounds."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 6 — Character Art  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def character_art_lessons():
    return [
        _lesson("Introduction to Character Design",
            """# Introduction to Character Design

Character design is the art of creating memorable, communicative visual characters for animation, games, comics, and illustration.

## What Makes a Great Character?
- **Strong silhouette**: Recognisable in pure black outline
- **Clear personality**: Visual design communicates who they are without words
- **Consistent design language**: Internal rules of proportion and style
- **Versatility**: Works across multiple contexts and poses

## Character Roles
Understanding the character's narrative role shapes their design:
- Hero: accessible, relatable forms
- Villain: sharp angles, dark palette, imposing scale
- Sidekick: rounder, softer, sometimes contrasting the hero

## Exercise
Sketch three character silhouettes for the same character concept at different emotional archetypes: friendly, menacing, comic. Compare how shape language communicates personality.""",
            "beginner", "character_art", 1, 35),

        _lesson("Human Body Proportions",
            """# Human Body Proportions

Accurate proportions are the foundation of believable character drawing.

## The Head as Unit of Measurement
The natural adult figure is 7–8 heads tall. Heroic/idealized figures are 8–9 heads. Cartoony figures can be 4–6 heads.

## Key Body Landmarks
- Chin to nipple line: 1 head
- Nipple to navel: 1 head
- Navel to crotch: 1 head
- Crotch to mid-thigh: 1 head
- Mid-thigh to knee: 1 head
- Knee to mid-calf: 1 head
- Mid-calf to ground: 1 head

## Shoulder Width
Male: ~2 head widths. Female: ~1.75 head widths. Hip width: comparable to shoulder width or slightly wider for female figures.

## Exercise
Draw a full figure in correct 7.5-head proportions, marking each head unit with horizontal alignment lines.""",
            "beginner", "character_art", 2, 40),

        _lesson("Shape Language in Characters",
            """# Shape Language in Characters

The shapes used to construct a character communicate personality before any detail is added.

## The Three Core Shapes
- **Circle/Curve**: Friendly, approachable, safe. Babies, comedic characters, gentle personalities.
- **Square/Box**: Stable, strong, trustworthy, reliable. Heroes, authority figures.
- **Triangle/Sharp**: Dangerous, deceptive, aggressive, villainous. Antagonists.

## Combining Shape Language
Most characters blend shapes to create nuanced personalities. A friendly but powerful hero might combine circular head with square torso.

## Feature-Level Shape Language
Shape language applies to every feature:
- Round eyes = innocent; angular eyes = intense or threatening
- Wide round nose = friendly; sharp pointed nose = cunning

## Exercise
Design three characters using only one dominant shape each: a pure circle character, a pure square character, and a pure triangle character.""",
            "beginner", "character_art", 3, 35),

        _lesson("Facial Expression Drawing",
            """# Facial Expression Drawing

The face is the primary vehicle for communicating a character's emotions and inner life.

## The Six Basic Expressions
Paul Ekman identified six universal facial expressions: happiness, sadness, anger, fear, surprise, and disgust.

## The Brow is Everything
The eyebrow angle and shape communicates more than any other facial feature. A slight V-shape = anger. Raised arches = surprise.

## Eye Shapes for Emotion
- Wide open: surprise, fear, wonder
- Narrowed: anger, suspicion, concentration
- Downturned outer corners: sadness
- Upturned outer corners: happiness

## Mouth Communication
Open and upturned = joy. Downturned corners = sadness. Compressed lips = restraint or anger.

## Exercise
Draw the same character face in all six basic expressions. Focus on brow angle and eye shape as the primary drivers.""",
            "beginner", "character_art", 4, 35),

        _lesson("Gesture Drawing for Characters",
            """# Gesture Drawing for Characters

Gesture is the underlying rhythm and movement of the figure — the living, dynamic force beneath anatomy.

## What is Gesture?
Gesture is the pose's main action line — also called the 'line of action'. A strong line of action makes characters feel alive.

## The Line of Action
A single curved or diagonal line running through the spine and neck describes the overall body attitude. Straight vertical = static. Curved = dynamic.

## C-Curves and S-Curves
- C-curve: one dominant bend in the spine — expressive, natural
- S-curve: opposing curves — walking, running, dynamic action

## Gesture Drawing Practice
Work quickly (30–60 second poses) to capture energy and movement, not detail. Use quick.pose.io or Line of Action for timed reference.

## Exercise
Complete 20 timed gesture drawings at 30 seconds each using an online reference tool. Focus only on the line of action.""",
            "beginner", "character_art", 5, 35),

        _lesson("Character Costume and Clothing Design",
            """# Character Costume and Clothing Design

Costume design communicates a character's world, status, personality, and culture at a glance.

## Costume as Character Language
- **Silhouette addition**: Capes, armour, and coats dramatically alter the character's overall silhouette
- **Material language**: Heavy armour = strength; loose flowing fabric = grace or magic
- **Cultural and period coding**: Costume instantly signals era and world

## Folds and Drape
Fabric folds always point toward a tension point (where the fabric is pulled). Common fold types: pull folds, drop folds, inert folds, pipe folds, zigzag folds.

## Practical vs Fantastical
Fantasy designs may defy physics but should maintain internal visual consistency. If a character wears impractical armour, the design should acknowledge the fantasy context.

## Exercise
Design two costumes for the same character: one practical/realistic and one fantastical. Note how each communicates differently.""",
            "intermediate", "character_art", 6, 55),

        _lesson("Hands and Feet Drawing",
            """# Hands and Feet Drawing

Hands and feet are among the most expressive but also most challenging parts of the figure.

## Hand Structure
Think of the hand as a block (the palm) with four sausages (fingers) and one opposing sausage (thumb) attached.

## Hand Proportions
The middle finger reaches approximately the halfway point of the palm's length. The thumb, when relaxed, aligns roughly with the base joint of the index finger.

## Common Hand Poses
- Relaxed open: fingers gently curled, not stiff and straight
- Fist: thumb wraps across the front, not tucked under
- Pointing: only index extends; the rest curl naturally

## Foot Structure
The foot is a wedge shape viewed from the side: high at the heel, sloping down to the toes. The arch lifts the inner edge off the ground.

## Exercise
Fill a page with 20 hand studies from your own hand using a mirror or photo reference. Draw 5 different poses including a relaxed open hand and a fist.""",
            "intermediate", "character_art", 7, 55),

        _lesson("Character Turnarounds",
            """# Character Turnarounds

A character turnaround (or model sheet) shows the character from multiple angles, ensuring visual consistency in animation and 3D modelling.

## Standard Views
- Front view: establishes width, height, and symmetry
- Side (profile) view: establishes depth and silhouette from the side
- Back view: hair and costume detail from behind
- Three-quarter view: most commonly used in practice

## Matching Heights (Registration Lines)
Horizontal registration lines drawn across all views ensure eyes, shoulders, waist, knees, and feet align consistently across views.

## Scale Comparison
If a cast of characters exists, turnarounds are drawn together at their correct relative heights to establish scale relationships.

## Exercise
Create a front / profile / back turnaround for an original character. Use horizontal registration lines to ensure consistent proportions across all three views.""",
            "intermediate", "character_art", 8, 60),

        _lesson("Dynamic Poses and Foreshortening",
            """# Dynamic Poses and Foreshortening

Foreshortening creates the illusion of depth when a limb or object points toward the viewer.

## What Is Foreshortening?
When a cylindrical form (arm, leg) points directly at the viewer, its apparent length compresses dramatically. An arm reaching toward the viewer looks very short in length but large in cross-section.

## Drawing Foreshortened Limbs
Build limbs as stacked cylinders or bounding boxes. Overlap the cylinders to reinforce depth. The far end of the limb appears smaller; the near end appears larger.

## Dynamic Pose Composition
- Keep the line of action strong and clear
- Create asymmetry: weight on one leg, arms at different heights
- Avoid symmetrical 'T-pose' unless intentional

## Exaggeration
Animation and action illustration often exaggerate poses well beyond realistic ranges for expressiveness and energy.

## Exercise
Draw the same character in three dynamic poses involving foreshortening: reaching toward viewer, running away, leaping upward.""",
            "intermediate", "character_art", 9, 65),

        _lesson("Character Art for Game and Animation",
            """# Character Art for Game and Animation

Professional character work for games and animation requires specific technical and artistic knowledge.

## Game Art Character Requirements
- **Sprite sheets** (2D): Characters drawn in all key animation states on one sheet
- **Concept art**: Multiple views, expressions, and colour calls for production
- **Silhouette readability**: At game resolution, character must be instantly readable

## Animation-Friendly Design
- Avoid overly complex details that cannot be animated
- Keep rigging zones (joints) clean — thick straps across joints cause deformation problems
- Secondary elements (hair, capes, tails) add animation richness without rigging complexity

## Style Consistency
A consistent style guide keeps a team of artists producing work that looks like it comes from the same world.

## LOD (Level of Detail)
Game characters have multiple LOD versions (high-res for close-ups, low-res for distant views) to manage performance.

## Exercise
Design a game-ready character concept: front view, back view, and 4 expression sheets. Include a colour palette swatch card.""",
            "advanced", "character_art", 10, 75),
    ]


def character_art_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "The most important quality of a strong character design silhouette is:",
           ["Being filled with internal detail", "Being immediately recognisable in pure black outline", "Having symmetrical shapes on both sides", "Including a visible costume element"],
           "Being immediately recognisable in pure black outline",
           "A strong silhouette communicates the character's identity instantly — even without colour or internal detail."),
        _q(l[0]["id"], "Sharp angles in a character design most commonly communicate:",
           ["Friendliness and warmth", "Danger, aggression, or villainy", "Reliability and stability", "Innocence and playfulness"],
           "Danger, aggression, or villainy",
           "Sharp, angular shapes create a visual language of threat and unpredictability, commonly used for villains and antagonists."),
        _q(l[0]["id"], "A hero character's visual design typically uses:",
           ["Sharp triangular shapes", "Exclusively circular features", "Accessible, relatable proportions and forms", "Very large scale to dominate the scene"],
           "Accessible, relatable proportions and forms",
           "Hero designs are typically approachable — relatable proportions and a balance of strong and friendly shapes help audiences identify with them."),
        _q(l[0]["id"], "A sidekick character is often visually designed to:",
           ["Look identical to the hero", "Contrast the hero in size, shape, or personality traits", "Always be taller than the hero", "Use darker colours than the villain"],
           "Contrast the hero in size, shape, or personality traits",
           "Sidekicks are often designed as visual counterpoints to the hero — contrast in size, shape, or temperament makes both characters more memorable."),
        _q(l[0]["id"], "Why is versatility an important quality in character design?",
           ["Characters should be redesigned to need many versions", "A versatile design works across multiple contexts, poses, and production scenarios", "Versatility means the character changes personality each scene", "It ensures no two characters look similar"],
           "A versatile design works across multiple contexts, poses, and production scenarios",
           "Characters appear in many situations; a design that only works in one specific pose or context creates production problems."),
    ]

    qs += [
        _q(l[1]["id"], "The standard natural adult figure measures approximately how many head heights tall?",
           ["4–5 heads", "6–7 heads", "7–8 heads", "10–12 heads"],
           "7–8 heads",
           "A naturally proportioned adult figure is 7–8 heads tall when using the head as a unit of measurement."),
        _q(l[1]["id"], "Heroic or idealised figure proportions are typically:",
           ["4–5 heads tall", "7 heads tall", "8–9 heads tall", "12 heads tall"],
           "8–9 heads tall",
           "Heroic figures are elongated to appear more imposing and idealised; comic book heroes are commonly 8–9 heads tall."),
        _q(l[1]["id"], "In traditional figure proportions, where does the halfway point of a 7.5-head figure fall?",
           ["At the navel", "At the waist", "At the crotch/hips", "At the knee"],
           "At the crotch/hips",
           "In a 7.5-head figure the halfway point is at the crotch — approximately 3.75 heads from both the top of the head and the soles of the feet."),
        _q(l[1]["id"], "When drawing a male figure, the shoulder width is approximately:",
           ["One head width", "Two head widths", "Three head widths", "Half head width"],
           "Two head widths",
           "The average adult male shoulder width is approximately two head widths — a key proportion used in figure construction."),
        _q(l[1]["id"], "Cartoony character proportions often use how many head heights?",
           ["7–8 heads", "8–9 heads", "4–6 heads", "10 or more heads"],
           "4–6 heads",
           "Shorter, bigger-headed cartoon proportions (4–6 heads) create a childlike, approachable, or exaggerated character feel."),
    ]

    qs += [
        _q(l[2]["id"], "In shape language, circular forms communicate:",
           ["Danger and aggression", "Friendliness, approachability, and safety", "Strength and authority", "Mystery and deception"],
           "Friendliness, approachability, and safety",
           "Circles and curves are associated with softness — babies, friendly animals, and comedic or gentle characters predominantly use rounded forms."),
        _q(l[2]["id"], "Triangular or sharp angular shapes in character design are associated with:",
           ["Trustworthiness and reliability", "Innocence and playfulness", "Danger, cunning, and villainy", "Calmness and balance"],
           "Danger, cunning, and villainy",
           "Sharp angles visually imply threat and instability — they are the dominant shape language of antagonists and dangerous characters."),
        _q(l[2]["id"], "Square and boxy shapes in character design communicate:",
           ["Playfulness and comedy", "Stability, strength, and reliability", "Mystery and elegance", "Speed and agility"],
           "Stability, strength, and reliability",
           "Square forms suggest solidity and reliability — they are commonly used for authority figures, heroes, and dependable character types."),
        _q(l[2]["id"], "Shape language in character design applies to:",
           ["Only the overall body silhouette", "The overall silhouette and individual features (eyes, nose, mouth)", "Only the costume elements", "Only the facial features"],
           "The overall silhouette and individual features (eyes, nose, mouth)",
           "Shape language is fractal — it applies consistently from the overall body silhouette down to individual facial features and costume details."),
        _q(l[2]["id"], "A friendly but powerful hero character would typically combine:",
           ["Triangular torso with circular head", "Circular or rounded head with square or boxy torso", "Triangular head with circular torso", "Fully angular body with no curved elements"],
           "Circular or rounded head with square or boxy torso",
           "Circular head = approachable and friendly; square torso = strong and reliable. The combination communicates both qualities simultaneously."),
    ]

    qs += [
        _q(l[3]["id"], "Which facial feature communicates emotion most powerfully in character drawing?",
           ["The nose", "The chin", "The eyebrows", "The ears"],
           "The eyebrows",
           "Eyebrow angle and shape are the single most powerful communicators of emotion — a subtle eyebrow change completely changes the expression."),
        _q(l[3]["id"], "Wide open eyes in a character expression typically communicate:",
           ["Anger and aggression", "Surprise, fear, or wonder", "Sadness and despair", "Suspicion and distrust"],
           "Surprise, fear, or wonder",
           "Wide open eyes expose more of the iris and white, signalling high arousal states: surprise, fear, excitement, or wonder."),
        _q(l[3]["id"], "Paul Ekman identified how many universal basic facial expressions?",
           ["Three", "Four", "Six", "Eight"],
           "Six",
           "Paul Ekman's research identified six cross-cultural universal expressions: happiness, sadness, anger, fear, surprise, and disgust."),
        _q(l[3]["id"], "Narrowed eyes in a character expression most commonly indicate:",
           ["Joy and happiness", "Surprise and wonder", "Anger, suspicion, or concentration", "Grief and sorrow"],
           "Anger, suspicion, or concentration",
           "Narrowing the eyes — squinting — is associated with focused negative emotions: anger, threat, suspicion, and intense concentration."),
        _q(l[3]["id"], "Downturned corners of the mouth in character expression communicate:",
           ["Joy and laughter", "Sadness, disappointment, or sorrow", "Surprise", "Determination"],
           "Sadness, disappointment, or sorrow",
           "The mouth corners pulling downward is a universally recognised indicator of sadness and negative emotional states."),
    ]

    qs += [
        _q(l[4]["id"], "The 'line of action' in gesture drawing is:",
           ["A reference line drawn around the entire figure", "The single primary curve or diagonal that captures the pose's overall energy", "A horizontal line at the character's eye level", "The outline of the character's silhouette"],
           "The single primary curve or diagonal that captures the pose's overall energy",
           "The line of action is an imaginary line running through the spine and neck; a strong, clear line makes the pose read with dynamic energy."),
        _q(l[4]["id"], "A straight vertical line of action in a character pose suggests:",
           ["Dynamic running action", "A relaxed, static, or neutral pose", "Extreme foreshortening", "An S-curve figure"],
           "A relaxed, static, or neutral pose",
           "A vertical line of action produces symmetrical, weight-balanced, static poses — the opposite of dynamic action."),
        _q(l[4]["id"], "Timed gesture drawing at 30-second intervals develops:",
           ["Fine detail rendering skill", "The ability to capture essential movement and energy quickly", "Accurate proportional measurement", "Slow, deliberate observational drawing"],
           "The ability to capture essential movement and energy quickly",
           "Short timed gestures force the artist to identify and capture the essential movement and feeling of a pose without getting caught up in detail."),
        _q(l[4]["id"], "An S-curve line of action suggests:",
           ["A completely static upright stance", "No body movement at all", "Flowing movement such as walking or a dancer's pose", "Extreme compression of the figure"],
           "Flowing movement such as walking or a dancer's pose",
           "S-curves create a sense of fluid movement with opposing directional forces — natural and graceful motion."),
        _q(l[4]["id"], "Gesture drawing is focused on capturing:",
           ["Accurate anatomical detail and muscles", "Texture and surface rendering", "The movement, rhythm, and living energy of the pose", "Precise proportional measurements"],
           "The movement, rhythm, and living energy of the pose",
           "Gesture is about the pose's essential quality — not accuracy. Training gesture builds the ability to make figures feel alive."),
    ]

    qs += [
        _q(l[5]["id"], "Fabric folds always originate from or point toward:",
           ["The nearest horizontal surface", "A tension point where the fabric is pulled, stretched, or supported", "The bottom of the garment", "The character's centre line"],
           "A tension point where the fabric is pulled, stretched, or supported",
           "Gravity and tension determine fold behaviour; understanding tension points (shoulders, elbows, knees, hips) makes clothing convincing."),
        _q(l[5]["id"], "In costume design, heavy plate armour communicates:",
           ["Grace and magical ability", "Strength, warfare capability, and physical power", "Wealth and nobility only", "Speed and agility"],
           "Strength, warfare capability, and physical power",
           "Heavy armour signals that the wearer is oriented toward physical combat — it communicates strength, defence, and martial power."),
        _q(l[5]["id"], "Adding a cape or large coat to a character design primarily affects:",
           ["Only the character's colour palette", "The character's overall silhouette shape and perceived scale", "Only the character's leg proportions", "The character's facial expression readability"],
           "The character's overall silhouette shape and perceived scale",
           "Large garments dramatically alter the silhouette, making characters appear larger, more powerful, or more dramatic."),
        _q(l[5]["id"], "When designing fantasy costumes that defy physical logic, the most important consideration is:",
           ["Ensuring the costume could theoretically be worn in reality", "Maintaining internal visual consistency within the fantasy design logic", "Avoiding all colour except black and grey", "Copying historical costume references exactly"],
           "Maintaining internal visual consistency within the fantasy design logic",
           "Fantasy designs have their own logic — elements should feel internally consistent even if impossible in reality."),
        _q(l[5]["id"], "Loose, flowing fabric in character design communicates:",
           ["Technical expertise and martial ability", "Grace, freedom, or magical connection", "Industrial strength and protection", "Speed and athletic ability only"],
           "Grace, freedom, or magical connection",
           "Flowing, lightweight garments suggest characters with elegance, supernatural ability, or a connection to natural or magical forces."),
    ]

    qs += [
        _q(l[6]["id"], "When constructing a hand, it is helpful to think of the palm as:",
           ["A curved oval shape", "A flat rectangular block with attached finger cylinders", "A series of individual connected squares", "Part of the wrist without a distinct structure"],
           "A flat rectangular block with attached finger cylinders",
           "Simplifying the palm as a block and fingers as cylinders/sausages makes the complex hand's structure manageable to construct and foreshorten."),
        _q(l[6]["id"], "The middle finger's tip reaches approximately where on the hand?",
           ["To the very end of the palm", "To the halfway point of the palm's length", "To the wrist joint", "Beyond the palm by half its length"],
           "To the halfway point of the palm's length",
           "The middle finger extends roughly the same length as the palm — its tip is at the midpoint of the total hand length."),
        _q(l[6]["id"], "In a relaxed open hand, the fingers should be drawn:",
           ["Perfectly straight and parallel", "Gently curled and slightly spread, not rigid", "Tightly gripped together", "Pointing all in different directions randomly"],
           "Gently curled and slightly spread, not rigid",
           "A truly relaxed hand has naturally slightly curled fingers — straight, stiff fingers look unnatural and rigid."),
        _q(l[6]["id"], "The foot viewed from the side is most accurately described as:",
           ["A flat rectangular shape", "A wedge shape: high at heel, sloping down to toes with an inner arch", "A circular disc", "Symmetrical on inner and outer edges"],
           "A wedge shape: high at heel, sloping down to toes with an inner arch",
           "The foot's wedge construction with a lifted arch on the inner edge is the key structural observation for drawing convincing feet."),
        _q(l[6]["id"], "When drawing a fist, the thumb should be positioned:",
           ["Tucked inside underneath the fingers", "Crossing in front of the curled fingers", "Pointing upward at 90°", "Inside the fist alongside the fingers"],
           "Crossing in front of the curled fingers",
           "In a properly formed fist, the thumb wraps across the front of the curled middle fingers — tucking it inside would result in injury."),
    ]

    qs += [
        _q(l[7]["id"], "A character turnaround (model sheet) is created to:",
           ["Show the character in extreme action poses", "Document the character from multiple angles for consistent reproduction", "Display all expression variations on one sheet", "Show how the character changes over time in the story"],
           "Document the character from multiple angles for consistent reproduction",
           "Turnarounds ensure that all animators, modellers, and production artists draw the character consistently from every angle."),
        _q(l[7]["id"], "Horizontal registration lines in a turnaround are used to:",
           ["Define the colour palette for the character", "Ensure key features align consistently across all views", "Set the line weight for the final linework", "Indicate which view is the primary one"],
           "Ensure key features align consistently across all views",
           "Registration lines drawn across all views (front, profile, back) guarantee that eyes, shoulders, waist, and feet match up correctly at the same height."),
        _q(l[7]["id"], "The four standard views included in a typical character turnaround are:",
           ["Top, bottom, left, right", "Front, side, back, and three-quarter", "Close-up, medium, wide, aerial", "Sketch, line art, colour, and shaded"],
           "Front, side, back, and three-quarter",
           "Front, profile (side), back, and three-quarter views form the standard set for animatable and 3D-moddable character turnarounds."),
        _q(l[7]["id"], "Scale comparison sheets in character art are used to:",
           ["Show the character at different ages", "Establish correct relative heights between multiple characters in a cast", "Compare amateur and professional artwork", "Show the character at different resolutions"],
           "Establish correct relative heights between multiple characters in a cast",
           "Scale comparison sheets place all cast members at their correct relative heights, establishing size relationships critical to storytelling and design."),
        _q(l[7]["id"], "The three-quarter view is most commonly used in character illustration because:",
           ["It requires the least amount of skill to draw", "It is the most dynamic and naturally readable angle showing both width and depth", "It is the standard for turnaround model sheets only", "It shows the character's back detail most clearly"],
           "It is the most dynamic and naturally readable angle showing both width and depth",
           "The three-quarter view suggests spatial depth and is the most commonly used viewing angle in illustrations, game sprites, and sequential art."),
    ]

    qs += [
        _q(l[8]["id"], "Foreshortening in figure drawing refers to:",
           ["Making distant characters smaller in a scene", "The visual compression of forms pointing toward or away from the viewer", "Reducing the character's height in the design", "Drawing figures with shorter bodies than realistic proportions"],
           "The visual compression of forms pointing toward or away from the viewer",
           "Foreshortening is perspective applied to the figure: forms pointing toward the viewer appear shorter but wider, creating depth."),
        _q(l[8]["id"], "When drawing a foreshortened arm reaching toward the viewer, it will appear:",
           ["Much longer and thinner than normal", "Short in length but large in cross-section at the near end", "Identical to a side-on arm view", "Invisible behind the torso"],
           "Short in length but large in cross-section at the near end",
           "A limb pointing directly at the viewer compresses in apparent length; the nearest part appears largest (perspective) while the far end is small."),
        _q(l[8]["id"], "Creating an asymmetrical pose (weight on one leg, arms at different heights) avoids:",
           ["Dynamic energy and movement", "The static, lifeless quality of symmetrical 'T-pose' stances", "Foreshortening opportunities", "Clear silhouette readability"],
           "The static, lifeless quality of symmetrical 'T-pose' stances",
           "Symmetrical poses appear static and artificial; weight shifts and limb asymmetry create organic, living poses."),
        _q(l[8]["id"], "In animation and action illustration, poses are often exaggerated to:",
           ["Reduce production costs", "Convey explosive energy and emotion beyond realistic physical limits", "Match photographic reference exactly", "Create realistic documentary-style work"],
           "Convey explosive energy and emotion beyond realistic physical limits",
           "Exaggerated poses push expressions and actions beyond realistic range, amplifying emotional and kinetic impact."),
        _q(l[8]["id"], "Overlapping cylinders in a foreshortened limb drawing helps to:",
           ["Add texture to the skin surface", "Create the illusion of depth through visual overlap", "Simplify the anatomy for clarity", "Define the line weight hierarchy"],
           "Create the illusion of depth through visual overlap",
           "Overlapping cylinders that decrease in size establish the spatial recession of a foreshortened limb convincingly."),
    ]

    qs += [
        _q(l[9]["id"], "A sprite sheet in 2D game character art is:",
           ["A high-resolution poster of the character", "All key animation states of a character arranged on a single image", "The character's concept art back view", "A colour palette reference sheet"],
           "All key animation states of a character arranged on a single image",
           "Sprite sheets organise all animation frames or states on one texture sheet, allowing the game engine to efficiently access each pose."),
        _q(l[9]["id"], "Animation-friendly character design avoids:",
           ["Secondary elements like capes and tails", "Clear rigging zones at joints", "Strong silhouette readability", "Overly complex costume details at joint areas that cause deformation artifacts"],
           "Overly complex costume details at joint areas that cause deformation artifacts",
           "Thick straps, buckles, or overlapping elements at joint regions cause visual problems when the skeleton deforms the mesh during animation."),
        _q(l[9]["id"], "Level of Detail (LOD) in game character art refers to:",
           ["The amount of expression detail on the face", "Multiple resolution versions of the character for performance management at different distances", "The hierarchy of design importance", "The complexity of the character's backstory"],
           "Multiple resolution versions of the character for performance management at different distances",
           "Game engines swap between LOD versions based on camera distance — high-detail models up close, simpler models in the distance — to maintain performance."),
        _q(l[9]["id"], "Secondary elements in character design (hair, capes, tails) are valued in animation because:",
           ["They simplify the rigging process", "They add animation richness and organic movement without complicating the main rig", "They are required for all character types", "They replace the need for primary body animation"],
           "They add animation richness and organic movement without complicating the main rig",
           "Secondary elements create compelling follow-through motion (a cape lagging behind a running hero) that makes characters feel physically weighty and alive."),
        _q(l[9]["id"], "A style guide for a game character team ensures:",
           ["Every artist produces unique, non-matching work", "All artists produce work with consistent visual language that belongs to the same world", "Characters look different from all other game art", "Only the lead artist's style is used"],
           "All artists produce work with consistent visual language that belongs to the same world",
           "A style guide documents the specific artistic decisions (line weight, colour range, proportion) so that multiple artists produce a cohesive visual work."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Category 7 — Sculpture  (10 lessons, 5 questions each)
# ---------------------------------------------------------------------------

def sculpture_lessons():
    return [
        _lesson("Introduction to Sculpture",
            """# Introduction to Sculpture

Sculpture is the art of creating three-dimensional objects through shaping or combining hard or plastic material.

## Major Sculpting Categories
- **Additive**: Building form by adding material (clay modelling, wax, digital sculpting)
- **Subtractive**: Cutting away material to reveal form (stone carving, wood carving)
- **Casting**: Creating a mould and filling it with liquid material that hardens
- **Assemblage**: Combining found or manufactured objects into new forms

## Common Materials
- Clay (oil-based or water-based)
- Stone (marble, limestone)
- Wood
- Metal (welded or cast)
- Polymer clay (Fimo, Sculpey)

## Basic Tools
Sculpture tools vary by medium: wire loop tools for clay, chisels for stone, welding torch for metal.

## Exercise
Using basic air-dry or polymer clay, sculpt a simple sphere, cube, and cylinder from scratch. Focus on clean planar surfaces.""",
            "beginner", "sculpture", 1, 35),

        _lesson("Clay Sculpting Fundamentals",
            """# Clay Sculpting Fundamentals

Clay is the most accessible sculpting medium — forgiving, responsive, and ideal for learning three-dimensional form.

## Types of Clay
- **Water-based clay**: Natural, cheap, must be kept moist. Can be fired in a kiln.
- **Oil-based clay (Plasteline/Chavant)**: Never dries. Ideal for maquettes and professional model-making.
- **Polymer clay (Sculpey/Fimo)**: Oven-hardening. Ideal for small figurines and detailed work.
- **Air-dry clay**: Dries without firing. Easier to access; more fragile than fired clay.

## Armature
For figures taller than 15cm, build an internal wire armature (skeleton) first. Without armature, tall forms collapse under their own weight.

## Working Process
1. Block out the largest primary masses
2. Add and define secondary forms
3. Final surface refinement and detail

## Exercise
Sculpt a simple human head from clay in three stages: rough egg form → major facial planes → refined features.""",
            "beginner", "sculpture", 2, 40),

        _lesson("Form and Volume in Sculpture",
            """# Form and Volume in Sculpture

Three-dimensional sculpture exists in real space — understanding form and volume is essential.

## Primary and Secondary Forms
- **Primary form**: The largest defining mass (e.g. the skull in a head sculpture)
- **Secondary form**: Smaller forms built on primary (brow ridge, cheekbones, jaw)
- **Tertiary form**: Fine surface details (pores, wrinkles, texture)

## Negative Space
The empty space surrounding and between sculptural forms is as important as the solid forms themselves. It defines silhouette and rhythm.

## Planar Analysis
Simplify any complex form into flat planes first. A human head has about 14 distinct planes. Plane-based construction prevents mushy, undefined form.

## Working in the Round
Rotate your sculpture constantly. A successful sculpture must read well from every angle — not just the front.

## Exercise
Sculpt a simple geometric head using only flat planes. No curves until the planes all read correctly from every angle.""",
            "beginner", "sculpture", 3, 40),

        _lesson("Sculpting Tools and Techniques",
            """# Sculpting Tools and Techniques

The right tool for the right task makes sculptural work faster and more precise.

## Essential Clay Tools
- **Wire loop tools**: Remove and hollow out clay, create recessed areas
- **Ball stylus**: Depress eye sockets and other concave areas
- **Wooden modelling tools**: Push and shape surface areas
- **Wire cutters / cheese wire**: Cut large pieces of clay cleanly
- **Spray bottle**: Keep water-based clay moist

## Surface Techniques
- **Smoothing**: Use a damp finger or silicone tool to blend joins
- **Texturing**: Press fabric, leaves, or custom texture stamps into soft clay
- **Carving**: Wait for clay to stiffen slightly, then carve with loop tools

## Scale Considerations
Fine tools for detailed areas; large fingers and palms for primary blocking.

## Exercise
Build a simple portrait head (approximately 10 cm tall) using at least 4 different tools. Document which tool you used for each stage.""",
            "beginner", "sculpture", 4, 40),

        _lesson("Anatomy for Sculptors",
            """# Anatomy for Sculptors

A sculptor must understand underlying bone and muscle structure — it creates the forms visible on the surface.

## The Skull
The skull is the primary form of the head. All soft tissue sits on top of the bony skull. Key landmarks: brow ridge, zygomatic arches (cheekbones), orbital rims, nasal bones, mandible (lower jaw).

## Muscles of the Face
- Orbicularis oculi: surrounds the eye
- Zygomaticus major: pulls the mouth corner up in smiling
- Masseter: jaw chewing muscle — creates the jaw's bulge
- Temporalis: temple muscle — visible as a slight indent at the temple

## The Torso
Built on the ribcage (egg shape) and pelvis (bowl shape) connected by the lumbar vertebrae. These two masses tilt and rotate relative to each other.

## Exercise
Study a skull reference image and sketch the 14 main planes of the skull. Then sculpt a basic skull shape from clay, identifying each plane.""",
            "beginner", "sculpture", 5, 45),

        _lesson("Figure Sculpting",
            """# Figure Sculpting

Sculpting the human figure combines proportion, anatomy, gesture, and surface artistry.

## Figure Armature
Assemble a wire armature using aluminium wire (or a professional steel armature for permanent pieces). The armature defines the pose before any clay is added.

## Blocking the Figure
Add clay in large chunks over the armature to establish:
1. Primary mass proportions (head, ribcage, pelvis, limbs)
2. Overall gesture and pose

## Building from Masses
- Ribcage: egg shape, slightly compressed laterally
- Pelvis: bowl or bucketshape, wider at the iliac crest
- Thighs: tapered cylinders widest at the top

## Checking Proportions
Use callipers or measuring tools to check head-to-height ratios throughout the process.

## Exercise
Build a small (15–20 cm) standing figure using an aluminium wire armature. Block in all major masses before adding any surface detail.""",
            "intermediate", "sculpture", 6, 60),

        _lesson("Surface Finishing and Texturing",
            """# Surface Finishing and Texturing

The surface of a sculpture — from ultra-smooth to roughly textured — is a major part of its character.

## Smoothing Techniques
- For oil clay: metal kidney-shaped scraper; solvent-moistened brush
- For water clay: firm sponge, rubber-rib tool, or wet fingers
- For polymer clay: smooth before baking; sand after baking with fine wet-and-dry sandpaper

## Creating Texture
- Hair: pull thin grooves with a dental tool or stiff bristle brush
- Fabric: press real fabric into soft clay or use texture stamps
- Skin: stipple surface with a stiff brush; use silicone skin texture sheets
- Rock/bark: scratch with crumpled aluminium foil or broken clay lumps

## Undercuts
Overhanging areas that create shadow are called undercuts. They add drama but complicate mould-making.

## Exercise
Sculpt three small 5cm tiles in clay each with a different surface texture: smooth, fabric-like, and rock-like. Photograph results.""",
            "intermediate", "sculpture", 7, 50),

        _lesson("Mould Making and Casting",
            """# Mould Making and Casting

Mould making allows a sculpture to be reproduced in materials more durable than the original clay.

## Why Make a Mould?
Clay originals are fragile and perishable. A mould captures the form and lets you cast in resin, plaster, wax, or bronze.

## Basic Mould Types
- **Press mould**: Simple one-sided mould for relief tiles
- **Two-part block mould**: Encases the sculpture in two halves of silicone
- **Glove mould**: Flexible silicone mould for complex undercuts

## Materials
- **Platinum silicone rubber**: Industry standard. Flexible, detail-capturing, durable.
- **Plaster of Paris**: Rigid mould material; used as a 'mother mould' outside a silicone jacket
- **Polyurethane resin**: Common casting material. Strong, lightweight.

## Basic Process
1. Build a containment wall around the model (mould box)
2. Pour silicone in layers
3. Cure, demould, cast

## Exercise
Create a simple one-piece press mould of a flat coin-sized relief sculpture using silicone putty. Cast several copies in plaster.""",
            "intermediate", "sculpture", 8, 60),

        _lesson("Stone and Wood Carving Basics",
            """# Stone and Wood Carving Basics

Subtractive sculpture — removing material — requires planning and commitment; you cannot add back what you remove.

## Stone Carving Materials
- **Soapstone**: Soft, easy to carve with basic tools. Good for beginners.
- **Alabaster**: Medium hardness, attractive translucency.
- **Limestone**: Medium hardness; widely used in traditional sculpture.
- **Marble**: Hard, crystalline, beautiful surface. Requires advanced technique.

## Stone Carving Tools
- **Point chisel**: Initial rough reduction
- **Tooth/claw chisel**: Intermediate shaping
- **Flat chisel**: Refining planes
- **Riffler**: Filing curved surfaces
- **Polishing grits**: Final surface polish

## Wood Carving
Carve with the grain when possible. Carving against the grain risks splitting. Basswood and butternut are soft, beginner-friendly woods.

## Subtractive Principle
First determine the largest form to carve away. Work from large to small — general to specific.

## Exercise
Carve a simple abstract form from a soft soapstone block using only a point chisel and a flat chisel.""",
            "intermediate", "sculpture", 9, 55),

        _lesson("Digital Sculpting Introduction",
            """# Digital Sculpting Introduction

Digital sculpting software allows artists to sculpt virtual three-dimensional forms using a pen tablet, combining the freedom of clay work with infinite undo capability.

## Popular Digital Sculpting Software
- **ZBrush**: The industry standard for character and creature sculpting
- **Blender (Sculpt Mode)**: Free and open-source, increasingly powerful
- **Nomad Sculpt**: iPad-based, excellent for concept sculpting

## Core Concepts
- **Subdivision levels**: Start sculpting on a low-poly base and add subdivision levels for finer detail
- **Dynamesh / Remesh**: Reconstruct topology as the form evolves, allowing addition and subtraction of mass freely
- **Brushes**: Move, Build, Inflate, Pinch, Trim Flat, Dam Standard — each behaves like a different sculpting tool

## Digital Advantages
- Infinite undo
- Non-destructive subdivision levels
- Scale reference objects inside the scene
- Direct export to 3D print or game engine

## Exercise
In Blender or ZBrush, begin with a sphere, subdivide 4 times, and sculpt a simple creature or human head using only 5 brushes.""",
            "advanced", "sculpture", 10, 65),
    ]


def sculpture_questions(lessons):
    l = lessons
    qs = []

    qs += [
        _q(l[0]["id"], "Additive sculpture refers to:",
           ["Cutting away material from a block", "Building form by adding material progressively", "Combining found objects", "Filling a mould with liquid material"],
           "Building form by adding material progressively",
           "Additive sculpture builds up form — clay modelling, digital sculpting, and wax work are all additive processes."),
        _q(l[0]["id"], "Subtractive sculpture differs from additive sculpture because:",
           ["It uses clay as the primary material", "Material is removed (carved or cut away) to reveal the form", "It requires a mould at every stage", "It produces hollow forms only"],
           "Material is removed (carved or cut away) to reveal the form",
           "Subtractive processes like stone carving and wood carving begin with a block and remove material to reveal the intended form."),
        _q(l[0]["id"], "Casting as a sculptural technique involves:",
           ["Building form with clay by hand", "Cutting a form from solid material", "Creating a mould and filling it with a liquid material that hardens", "Welding metal pieces together"],
           "Creating a mould and filling it with a liquid material that hardens",
           "Casting captures a mould of the original and allows it to be reproduced in materials such as bronze, plaster, or resin."),
        _q(l[0]["id"], "Which clay type is best suited for professional maquette and model-making because it never dries?",
           ["Water-based clay", "Air-dry clay", "Oil-based clay (Plasteline/Chavant)", "Polymer clay"],
           "Oil-based clay (Plasteline/Chavant)",
           "Oil-based clays stay workable indefinitely at room temperature, making them ideal for professional sculptors who need to rework pieces over extended periods."),
        _q(l[0]["id"], "Assemblage sculpture is characterised by:",
           ["Carving a single block of material", "Combining found or manufactured objects into a new form", "Casting all elements from a single mould", "Building only in clay and plaster"],
           "Combining found or manufactured objects into a new form",
           "Assemblage uses pre-existing objects (driftwood, machine parts, everyday items) combined into new sculptural compositions."),
    ]

    qs += [
        _q(l[1]["id"], "Why is an armature necessary when sculpting tall figures in clay?",
           ["It speeds up the surface finishing process", "It provides an internal skeleton preventing the sculpture from collapsing under its own weight", "It helps to keep water-based clay moist", "It determines the scale of the final figure"],
           "It provides an internal skeleton preventing the sculpture from collapsing under its own weight",
           "Tall clay figures without internal support collapse as clay is heavy; an armature (typically wire) provides structural backbone."),
        _q(l[1]["id"], "The correct working process for sculpting a figure from clay is:",
           ["Final detail → secondary forms → primary masses", "Primary masses → secondary forms → final surface detail", "Surface detail everywhere at equal priority", "Secondary forms → detail → primary masses"],
           "Primary masses → secondary forms → final surface detail",
           "Working from largest to smallest ensures the foundational form is correct before investing time in lower-level detail."),
        _q(l[1]["id"], "Polymer clay (Sculpey/Fimo) is hardened by:",
           ["Air drying over 24 hours", "Firing in a professional kiln", "Baking in a domestic oven", "Submerging in water"],
           "Baking in a domestic oven",
           "Polymer clay cures through heat polymerisation at relatively low oven temperatures (typically 110–130°C), accessible in a domestic oven."),
        _q(l[1]["id"], "Water-based clay must be kept moist during sculpting because:",
           ["It gains hardness as it stays moist", "It cracks and becomes unworkable if it dries out before completion", "It expands when dry, changing the proportions", "It requires moisture to retain its colour"],
           "It cracks and becomes unworkable if it dries out before completion",
           "Water-based clay begins to shrink and crack as it dries; regular misting with a spray bottle keeps it workable during long sessions."),
        _q(l[1]["id"], "Compared to fired clay, air-dry clay is generally:",
           ["Stronger and more durable", "More fragile and less water-resistant", "Identical in properties after drying", "Harder and more resistant to breakage"],
           "More fragile and less water-resistant",
           "Air-dry clay produces a weaker, more porous result than kiln-fired ceramic — it is more accessible but less durable."),
    ]

    qs += [
        _q(l[2]["id"], "Primary forms in sculpture refer to:",
           ["The finest surface details and texture", "The largest defining masses — the main overall shape", "Decorative surface embellishments", "The internal armature structure"],
           "The largest defining masses — the main overall shape",
           "Primary forms are the largest, most fundamental shapes: the skull's overall egg form, the ribcage mass, the pelvis block — everything else is built on these."),
        _q(l[2]["id"], "Planar analysis in sculpture means:",
           ["Analysing the colour planes of a painted surface", "Simplifying complex forms into flat planes to define structure clearly", "Taking measurements from a reference plane", "Carving only flat-surfaced abstract forms"],
           "Simplifying complex forms into flat planes to define structure clearly",
           "Breaking a form into flat planes before adding curves prevents mushy, undefined work and clarifies the underlying structure."),
        _q(l[2]["id"], "Negative space in three-dimensional sculpture is:",
           ["The darkest areas of the sculpture's surface", "The empty space surrounding and between solid forms", "The area carved away in subtractive work", "The part of the armature that is not covered"],
           "The empty space surrounding and between solid forms",
           "Negative space in sculpture is the air around and between solid masses — it defines silhouette, rhythm, and overall visual balance."),
        _q(l[2]["id"], "Rotating a sculpture regularly during the work process is important because:",
           ["It prevents the clay from drying unevenly", "A successful sculpture must read well from every angle, not just the front", "It helps the armature stay stable", "Rotation automatically reveals where more clay is needed"],
           "A successful sculpture must read well from every angle, not just the front",
           "Unlike a painting, sculpture is viewed from all sides; an unrotated work often develops well on the front but has unresolved forms on other sides."),
        _q(l[2]["id"], "Tertiary forms in sculpture are:",
           ["The largest primary masses", "Fine surface details — the smallest level of form (pores, wrinkles, surface texture)", "The joints between the armature sections", "Secondary anatomical structures"],
           "Fine surface details — the smallest level of form (pores, wrinkles, surface texture)",
           "The hierarchy runs: primary (large mass) → secondary (medium features) → tertiary (fine surface detail). Tertiary forms are added last."),
    ]

    qs += [
        _q(l[3]["id"], "A wire loop tool is primarily used in clay sculpting to:",
           ["Smooth the surface to a high finish", "Remove clay and hollow out areas, creating recessed forms", "Create fine linear hair textures", "Hold the clay to a work surface"],
           "Remove clay and hollow out areas, creating recessed forms",
           "Loop tools cut into and remove clay, essential for hollowing, refining concave areas, and carving detail."),
        _q(l[3]["id"], "When should a sculptor begin carving detail into clay?",
           ["As the very first step after assembling the armature", "Only after allowing the clay to stiffen slightly", "Only when the clay has completely hardened", "Before the primary forms are fully resolved"],
           "Only after allowing the clay to stiffen slightly",
           "Slightly stiffened clay holds its edges better than very soft fresh clay, making detail carving and refining more precise."),
        _q(l[3]["id"], "Which principle should guide tool selection during a clay sculpting session?",
           ["Always use the same tool for consistency", "Small fine tools throughout for even detail across the sculpture", "Large tools for blocking; smaller fine tools for detail", "Use only fingers to preserve direct control"],
           "Large tools for blocking; smaller fine tools for detail",
           "Matching tool size to the scale of the work being done at each stage ensures efficiency: large tools establish mass quickly, fine tools refine detail."),
        _q(l[3]["id"], "Pressing real fabric into soft clay creates:",
           ["A smooth reflective surface", "A fabric-like texture impression in the clay surface", "Deep undercuts requiring mould work", "Relief carving on the surface"],
           "A fabric-like texture impression in the clay surface",
           "Pressing textured objects (fabric, leaves, wire mesh) into soft clay transfers their surface pattern as an impression."),
        _q(l[3]["id"], "For a water-based clay sculpture, keeping a spray bottle nearby helps to:",
           ["Add colour to the clay surface", "Keep the clay moist and workable during long sessions", "Clean tools between uses", "Soften polymer clay for detail work"],
           "Keep the clay moist and workable during long sessions",
           "Regular light misting prevents the outer clay surface from drying and cracking during extended work sessions."),
    ]

    qs += [
        _q(l[4]["id"], "In sculpting the human head, the skull serves as:",
           ["A reference image only", "The primary form upon which all soft tissue sits", "The secondary form after the face muscles are added", "An optional consideration for detail work"],
           "The primary form upon which all soft tissue sits",
           "The skull is the primary architectural form of the head — every muscle, fat pad, and surface feature sits on top of this foundational bony structure."),
        _q(l[4]["id"], "The zygomatic arches in facial anatomy are the:",
           ["Brow ridges above the eyes", "Cheekbones — the widest area of the face", "Orbital rims around the eye sockets", "Lower jaw / mandible"],
           "Cheekbones — the widest area of the face",
           "The zygomatic arches are the cheekbones — their prominence determines how wide the face appears and creates the distinctive mid-face plane."),
        _q(l[4]["id"], "The torso's major masses consist of:",
           ["Spine, shoulders, arms, and legs", "Ribcage and pelvis connected by the lumbar spine", "Sternum, navel, and hips as equal masses", "One unified cylindrical mass"],
           "Ribcage and pelvis connected by the lumbar spine",
           "The torso's two primary masses — the egg-shaped ribcage and the bowl-shaped pelvis — tilt and rotate relative to each other, creating all torso movements."),
        _q(l[4]["id"], "The masseter muscle in facial anatomy is responsible for:",
           ["Raising the eyebrow", "Pulling the mouth corner upward", "Jaw clenching and chewing — the large jaw muscle", "Controlling eye blinking"],
           "Jaw clenching and chewing — the large jaw muscle",
           "The masseter is the powerful chewing muscle; it is visible as a bulge at the rear angle of the jaw and is important for sculpting a convincing jaw area."),
        _q(l[4]["id"], "The mandible in facial anatomy is the:",
           ["Upper jaw / maxilla", "Cheekbone", "Lower jaw", "Eye socket ridge"],
           "Lower jaw",
           "The mandible is the lower jaw — the only independently moveable facial bone. It defines the lower third of the face and determines jaw shape."),
    ]

    qs += [
        _q(l[5]["id"], "When building a figure armature, aluminium wire is preferred over steel because:",
           ["It is cheaper than all other materials", "It is easy to bend and repose without special tools", "It provides more strength for large-scale figures", "It never needs to be covered with clay"],
           "It is easy to bend and repose without special tools",
           "Aluminium wire is soft enough to bend by hand, allowing the armature pose to be adjusted throughout the sculpting process."),
        _q(l[5]["id"], "The pelvis form in figure sculpting is best described as:",
           ["A narrow vertical cylinder", "A wide egg shape", "A bowl or bucket shape with wider iliac crest", "A flat horizontal disc"],
           "A bowl or bucket shape with wider iliac crest",
           "The pelvis is a roughly bucket-shaped mass, wider at the top (iliac crests) — this shape anchors the lower torso and connects to the legs."),
        _q(l[5]["id"], "Callipers are used in figure sculpting to:",
           ["Apply smooth surface finishes", "Measure and check head-to-body proportion ratios during sculpting", "Mix clay colours evenly", "Create texture patterns on the surface"],
           "Measure and check head-to-body proportion ratios during sculpting",
           "Callipers transfer measurements from reference or between parts of the sculpture, ensuring proportions remain accurate throughout the process."),
        _q(l[5]["id"], "The ribcage in figure sculpting is approximated as:",
           ["A flat rectangular plane", "A wide cylinder", "An egg or barrel shape", "A perfectly round sphere"],
           "An egg or barrel shape",
           "The ribcage is an egg-shaped form — slightly tapered at the top (sternum/clavicles), fuller in the middle, and narrowing toward the lower ribs."),
        _q(l[5]["id"], "Why must primary mass proportions be established before surface detail in figure sculpting?",
           ["It is faster to detail before adding mass", "Incorrect underlying proportions cannot be fixed after surface detail is added without losing that detail", "Surface detail helps identify proportion errors", "Proportion is less important in figurative sculpture"],
           "Incorrect underlying proportions cannot be fixed after surface detail is added without losing that detail",
           "Solving proportion problems after detailed surface work has been added requires destroying that surface work — it is far more efficient to confirm proportions early."),
    ]

    qs += [
        _q(l[6]["id"], "When smoothing oil-based clay, the best tool to use is:",
           ["Wet fingers or a water-moistened sponge", "A metal kidney-shaped scraper or solvent-moistened brush", "An air compressor", "A heat gun"],
           "A metal kidney-shaped scraper or solvent-moistened brush",
           "Oil-based clay is smoothed with metal kidney scrapers or brushes lightly dampened with solvent (naphtha/mineral spirits), not water."),
        _q(l[6]["id"], "Undercuts in sculpture are surfaces that:",
           ["Slope upward from the base", "Overhang and create shadow beneath them", "Require extra clay to fill in", "Describe the lowest flat surface"],
           "Overhang and create shadow beneath them",
           "Undercuts are recessed areas under projecting forms; they add shadow and drama but complicate mould-making because flexible silicone is needed to release them."),
        _q(l[6]["id"], "To create a hair-like texture in clay, you would use:",
           ["Pressing real fabric into the surface", "Pulling thin grooves with a dental tool or stiff bristle brush", "Smoothing with a damp sponge", "Pressing aluminium foil into the surface"],
           "Pulling thin grooves with a dental tool or stiff bristle brush",
           "Fine hair texture is created by dragging pointed tools along the clay surface in the direction of hair flow, creating series of parallel grooves."),
        _q(l[6]["id"], "Stippling the surface of clay with a stiff brush creates:",
           ["A smooth polished finish", "A skin-like pore texture", "Deep carved-out lines", "A metallic reflective surface"],
           "A skin-like pore texture",
           "Stippling (dabbing the stiff brush tip repeatedly) creates an irregular dotted texture that resembles the fine pore structure of skin."),
        _q(l[6]["id"], "After baking polymer clay, achieving a very smooth surface requires:",
           ["Immediately painting with acrylic", "Sanding with progressively finer wet-and-dry sandpaper after baking", "Re-baking at a higher temperature", "Applying silicone release spray"],
           "Sanding with progressively finer wet-and-dry sandpaper after baking",
           "Polymer clay can be wet-sanded after baking through progressively finer grits (400, 600, 800, 1200, 2000) to achieve a smooth or glass-like surface."),
    ]

    qs += [
        _q(l[7]["id"], "The primary reason to create a mould of a clay sculpture is:",
           ["To preserve the original clay permanently", "To reproduce the sculpture in a more durable or permanent material", "To reduce the sculpture's weight", "To prepare it for digital scanning only"],
           "To reproduce the sculpture in a more durable or permanent material",
           "Clay originals are fragile; casting from a mould produces durable replicas in resin, plaster, wax, or bronze."),
        _q(l[7]["id"], "Platinum silicone rubber is used for professional sculpture moulds because:",
           ["It is the cheapest mould material available", "It is flexible (captures undercuts), detail-capturing, and durable for many casts", "It requires no cure time", "It is rigid, preventing dimensional change"],
           "It is flexible (captures undercuts), detail-capturing, and durable for many casts",
           "Platinum silicone captures fine surface detail, flexes to release undercuts, and can produce dozens of casts before wearing out — the professional standard."),
        _q(l[7]["id"], "A 'mother mould' in the casting process is:",
           ["The original clay sculpture", "A rigid outer shell (usually plaster) that holds the flexible silicone mould in the correct shape", "The first cast produced from a new mould", "A reusable rubber block mould"],
           "A rigid outer shell (usually plaster) that holds the flexible silicone mould in the correct shape",
           "Flexible silicone would sag without support; the rigid plaster mother mould holds it in the correct shape during the casting pour."),
        _q(l[7]["id"], "A two-part block mould is used when:",
           ["The sculpture is extremely thin and flat", "The sculpture is a simple, single-sided relief tile", "The sculpture is three-dimensional and cannot be released from a single-piece mould", "The casting material is water-based only"],
           "The sculpture is three-dimensional and cannot be released from a single-piece mould",
           "Two-part moulds split at a defined parting line to allow release of fully three-dimensional forms that a one-piece mould could not release."),
        _q(l[7]["id"], "Polyurethane resin is commonly used as a casting material because:",
           ["It is identical to bronze in appearance", "It is strong, lightweight, and takes paint and patinas well", "It requires a kiln to cure", "It can only be used for small objects under 5cm"],
           "It is strong, lightweight, and takes paint and patinas well",
           "Polyurethane resin cures at room temperature, produces strong lightweight castings, and can be painted, pigmented, or chemically patinated."),
    ]

    qs += [
        _q(l[8]["id"], "Which stone is most recommended for beginner stone carvers because of its softness?",
           ["Marble", "Granite", "Soapstone", "Basalt"],
           "Soapstone",
           "Soapstone (steatite) is a very soft stone (hardness ~1–2 on the Mohs scale) easily carved with basic tools — ideal for beginners."),
        _q(l[8]["id"], "The point chisel in stone carving is used for:",
           ["Final surface polishing", "Refining flat planes", "Initial rough reduction and removing large amounts of material", "Filing curved surfaces"],
           "Initial rough reduction and removing large amounts of material",
           "The point chisel is the first tool used in stone carving — its pointed impact concentrates force to knock off large chunks quickly."),
        _q(l[8]["id"], "In wood carving, why should you generally carve with the grain?",
           ["Carving with the grain produces a better texture", "Carving against the grain risks splitting the wood along structural fibres", "Modern tools only cut effectively with the grain", "It is easier to achieve fine detail with the grain"],
           "Carving against the grain risks splitting the wood along structural fibres",
           "Wood fibres run in one direction; cutting against them causes the wood to split unpredictably, whereas carving with the grain follows natural cleavage lines safely."),
        _q(l[8]["id"], "The subtractive principle in stone and wood carving requires:",
           ["Adding material to fill mistakes", "Planning the final form before starting, as removed material cannot be replaced", "Starting with the finest details and working outward", "Using the same tool for all stages of the carving"],
           "Planning the final form before starting, as removed material cannot be replaced",
           "Once material is removed in subtractive carving, it cannot be replaced — careful planning and working from large forms to small prevents irreversible mistakes."),
        _q(l[8]["id"], "The tooth (claw) chisel in stone carving is used for:",
           ["Initial rough reduction of large masses", "Intermediate shaping after the point chisel stage", "Final polishing of the surface", "Creating deep undercut areas"],
           "Intermediate shaping after the point chisel stage",
           "The tooth chisel follows the point chisel — its multiple teeth remove stone in a controlled way, refining the rough form toward the intended final shape."),
    ]

    qs += [
        _q(l[9]["id"], "ZBrush is known in digital sculpting as:",
           ["A free open-source tool for beginners only", "The industry standard for character and creature digital sculpting", "Primarily a 2D painting application with limited 3D features", "A web-based sculpting tool requiring no installation"],
           "The industry standard for character and creature digital sculpting",
           "ZBrush dominates professional character, creature, and organic sculpting pipelines in film, games, and collectibles."),
        _q(l[9]["id"], "Subdivision levels in digital sculpting allow:",
           ["Starting with fine detail and working toward overall form", "Adding more polygon resolution progressively for finer and finer detail", "Reducing file size for export", "Converting sculpt data to vector paths"],
           "Adding more polygon resolution progressively for finer and finer detail",
           "Subdivision multiplies the polygon count, providing more surface density to sculpt finer forms without losing the lower-level base shape."),
        _q(l[9]["id"], "Dynamesh / Remesh in ZBrush and Blender is useful because:",
           ["It automatically textures the sculpt", "It reconstructs the topology as you add or remove mass, preventing stretched polygons", "It locks the sculpt to prevent accidental changes", "It exports the model for 3D printing automatically"],
           "It reconstructs the topology as you add or remove mass, preventing stretched polygons",
           "When you significantly add or subtract clay-like mass digitally, polygon density becomes uneven; Dynamesh re-distributes polygons evenly across the new form."),
        _q(l[9]["id"], "The primary advantage of digital sculpting over physical clay sculpting is:",
           ["Digital sculpts always look photo-realistic", "Infinite undo, non-destructive subdivision levels, and no material cost", "Digital sculpting requires no artistic skill", "Physical results are directly produced without printing"],
           "Infinite undo, non-destructive subdivision levels, and no material cost",
           "Digital sculpting allows complete reversibility (undo history), non-destructive workflow (subdivision levels), and no material costs — powerful advantages over physical media."),
        _q(l[9]["id"], "Which free, open-source software includes a sculpting mode suitable for digital sculpture?",
           ["ZBrush", "Nomad Sculpt", "Blender", "Maya"],
           "Blender",
           "Blender is a free, open-source 3D suite that includes a fully featured sculpting mode with brushes, masking, and remeshing tools."),
    ]

    return qs


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

def create_sample_data(reset=False):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        if reset:
            print("Resetting lessons and quiz questions...")
            db.query(QuizQuestion).delete()
            db.query(Lesson).delete()
            db.commit()
            print("Reset complete.")
        else:
            existing = db.query(Lesson).first()
            if existing:
                print("Sample data already exists. Run with --reset to re-seed.")
                return

        print("Creating sample data...")

        # ── Users ──────────────────────────────────────────────────────────
        demo_user = db.query(User).filter(User.email == "demo@artbuddy.com").first()
        if not demo_user:
            demo_user_id = str(uuid.uuid4())
            db.add(User(
                id=demo_user_id,
                name="Demo User",
                email="demo@artbuddy.com",
                hashed_password=get_password_hash("password123"),
                skill_level="beginner",
                created_at=datetime.utcnow(),
            ))
        else:
            demo_user_id = str(demo_user.id)

        if not db.query(User).filter(User.email == "student@artbuddy.com").first():
            db.add(User(
                id=str(uuid.uuid4()),
                name="Art Student",
                email="student@artbuddy.com",
                hashed_password=get_password_hash("student123"),
                skill_level="intermediate",
                created_at=datetime.utcnow(),
            ))

        # ── Lessons & Quiz Questions ───────────────────────────────────────
        all_category_fns = [
            (drawing_lessons,      drawing_questions),
            (painting_lessons,     painting_questions),
            (color_theory_lessons, color_theory_questions),
            (digital_art_lessons,  digital_art_questions),
            (design_lessons,       design_questions),
            (character_art_lessons,character_art_questions),
            (sculpture_lessons,    sculpture_questions),
        ]

        total_lessons = 0
        total_questions = 0

        for lesson_fn, question_fn in all_category_fns:
            cat_lessons = lesson_fn()
            if not cat_lessons:
                continue
            for ld in cat_lessons:
                db.add(Lesson(**ld))
            cat_questions = question_fn(cat_lessons)
            for qd in cat_questions:
                db.add(QuizQuestion(**qd))
            total_lessons += len(cat_lessons)
            total_questions += len(cat_questions)

        db.flush()

        # ── Progress for demo user ─────────────────────────────────────────
        first_lesson = db.query(Lesson).first()
        if first_lesson and demo_user_id:
            db.add(Progress(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                lesson_id=first_lesson.id,
                completion_status="completed",
                score=85.0,
                time_spent_minutes=28,
                completed_at=datetime.utcnow() - timedelta(days=2),
                created_at=datetime.utcnow() - timedelta(days=2),
            ))

        # ── Reminders ─────────────────────────────────────────────────────
        db.add(Reminder(
            id=str(uuid.uuid4()),
            user_id=demo_user_id,
            title="Daily Drawing Practice",
            message="Keep your skills sharp — 30 minutes of practice today!",
            reminder_type="daily_practice",
            schedule_time=datetime.utcnow() + timedelta(hours=2),
            is_sent=False,
            created_at=datetime.utcnow(),
        ))

        db.commit()

        print(f"\n✅ Seeding complete!")
        print(f"   Lessons  : {total_lessons}")
        print(f"   Questions: {total_questions}")
        print(f"\n🎨 Login: demo@artbuddy.com / password123")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback; traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    create_sample_data(reset=reset)
