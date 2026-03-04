#!/usr/bin/env python3
"""List all lessons with quiz questions"""
from app.database import SessionLocal
from app.entities.models import QuizQuestion, Lesson

db = SessionLocal()

# Get all lessons with quiz questions
quiz_questions = db.query(QuizQuestion).all()

lesson_ids_with_quizzes = list(set([q.lesson_id for q in quiz_questions]))

print(f'Found {len(lesson_ids_with_quizzes)} lessons with quizzes:\n')

for lesson_id in lesson_ids_with_quizzes:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    quiz_count = db.query(QuizQuestion).filter(QuizQuestion.lesson_id == lesson_id).count()
    print(f'  ✓ {lesson.title}')
    print(f'    ID: {lesson_id}')
    print(f'    Questions: {quiz_count}')
    print()

db.close()
