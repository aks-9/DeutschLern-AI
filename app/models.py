from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Represents a registered user of the application."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    level = Column(String(2), default="A1")
    created_at = Column(DateTime, default=datetime.utcnow)

    vocab_entries = relationship("VocabularyEntry", back_populates="user")
    coach_sessions = relationship("CoachSession", back_populates="user")


class GrammarTopic(Base):
    """A grammar lesson topic, seeded into the DB by level."""

    __tablename__ = "grammar_topics"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    level = Column(String(2), nullable=False)
    content = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)


class Exercise(Base):
    """An AI-generated exercise, cached in the DB per topic."""

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("grammar_topics.id"))
    level = Column(String(2), nullable=False)
    type = Column(String(20), nullable=False)
    question_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExerciseAttempt(Base):
    """Records a single user attempt at an exercise."""

    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    user_answer = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    attempted_at = Column(DateTime, default=datetime.utcnow)


class VocabularyEntry(Base):
    """A word saved by a user to their personal vocabulary list."""

    __tablename__ = "vocabulary_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String(255), nullable=False)
    meaning = Column(Text, nullable=False)
    gender = Column(String(10))
    example_sentence = Column(Text)
    level = Column(String(2))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vocab_entries")


class CoachSession(Base):
    """A single conversation session with the AI coach."""

    __tablename__ = "coach_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scenario = Column(String(100))
    started_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="coach_sessions")
    messages = relationship("CoachMessage", back_populates="session")


class CoachMessage(Base):
    """A single message within a coach session, from user or assistant."""

    __tablename__ = "coach_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("coach_sessions.id"))
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("CoachSession", back_populates="messages")
