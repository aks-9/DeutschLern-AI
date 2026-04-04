"""Tests for ai_service.py — generate_exercise(), grade_answer(), generate_quick_check()."""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_service import (
    generate_exercise,
    grade_answer,
    generate_quick_check,
)


# -- Helper -------------------------------------------------------------------

def make_mock_response(content: dict) -> MagicMock:
    """Build a fake OpenAI chat completion response.

    :param content: Dict to encode as the message content JSON string.
    :return: MagicMock shaped like an OpenAI ChatCompletion object.
    """
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps(content) #converts a Python dict to a JSON string — because that's what OpenAI actually returns (a string, not a dict).
                )
            )
        ]
    )


# -- generate_exercise() ------------------------------------------------------

def test_generate_exercise_returns_required_keys():
    """generate_exercise() must return sentence, blank_word, hint, explanation."""
    fake_response = make_mock_response({
        "sentence": "Ich ___ ein Student.",
        "blank_word": "bin",
        "hint": "verb to be, first person",
        "explanation": "bin is the ich-form of sein."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        result = generate_exercise("Articles", "A1")

    assert "sentence" in result
    assert "blank_word" in result
    assert "hint" in result
    assert "explanation" in result


def test_generate_exercise_uses_correct_model():
    """generate_exercise() must call GPT-4o-mini, not the full GPT-4o."""
    fake_response = make_mock_response({
        "sentence": "Er ___ Deutsch.",
        "blank_word": "lernt",
        "hint": "present tense verb",
        "explanation": "lernt is the er-form of lernen."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        generate_exercise("Verbs", "A1")

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs #lets us inspect exactly what arguments were passed to the fake API call.
    assert call_kwargs["model"] == "gpt-4o-mini"


# ensures we handle bad API responses gracefully instead of crashing with a confusing error.
def test_generate_exercise_invalid_json_raises():
    """generate_exercise() must raise ValueError if OpenAI returns invalid JSON."""
    bad_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content="not valid json"))]
    ) #building a fake object that looks like a real OpenAI response layer by layer: response.choices[0].message.content

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = bad_response
        with pytest.raises(ValueError):
            generate_exercise("Articles", "A1")


# -- grade_answer() -----------------------------------------------------------

def test_grade_answer_returns_required_keys():
    """grade_answer() must return correct, score, and feedback."""
    fake_response = make_mock_response({
        "correct": True,
        "score": 1.0,
        "feedback": "Perfect! 'bin' is correct."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        result = grade_answer(
            sentence="Ich ___ ein Student.",
            blank_word="bin",
            user_answer="bin",
            level="A1"
        )

    assert "correct" in result
    assert "score" in result
    assert "feedback" in result


def test_grade_answer_uses_correct_model():
    """grade_answer() must call GPT-4o-mini."""
    fake_response = make_mock_response({
        "correct": False,
        "score": 0.0,
        "feedback": "Not quite — 'bist' is for 'du', not 'ich'."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        grade_answer(
            sentence="Ich ___ ein Student.",
            blank_word="bin",
            user_answer="bist",
            level="A1"
        )

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"


# -- generate_quick_check() ---------------------------------------------------

def test_quick_check_returns_required_keys():
    """generate_quick_check() must return question, options, correct_index, explanation."""
    fake_response = make_mock_response({
        "question": "Which article goes with 'Mann'?",
        "options": ["der", "die", "das", "den"],
        "correct_index": 0,
        "explanation": "'Mann' is masculine, so the nominative article is 'der'."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        result = generate_quick_check("German Articles", "A1")

    assert "question" in result
    assert "options" in result
    assert "correct_index" in result
    assert "explanation" in result


def test_quick_check_options_is_list_of_four():
    """generate_quick_check() must return exactly 4 options."""
    fake_response = make_mock_response({
        "question": "Which article goes with 'Frau'?",
        "options": ["der", "die", "das", "dem"],
        "correct_index": 1,
        "explanation": "'Frau' is feminine, so the article is 'die'."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        result = generate_quick_check("German Articles", "A1")

    assert isinstance(result["options"], list)
    assert len(result["options"]) == 4


def test_quick_check_correct_index_in_range():
    """generate_quick_check() correct_index must be 0, 1, 2, or 3."""
    fake_response = make_mock_response({
        "question": "Which is the plural of 'Kind'?",
        "options": ["Kinds", "Kinder", "Kindes", "Kinden"],
        "correct_index": 1,
        "explanation": "The plural of 'Kind' is 'Kinder'."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        result = generate_quick_check("Plural Nouns", "A1")

    assert result["correct_index"] in range(4)


def test_quick_check_uses_correct_model():
    """generate_quick_check() must call GPT-4o-mini."""
    fake_response = make_mock_response({
        "question": "What is the correct verb form?",
        "options": ["bin", "bist", "ist", "sind"],
        "correct_index": 0,
        "explanation": "'bin' is the ich-form of sein."
    })

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_response
        generate_quick_check("Verb Conjugation", "A1")

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"


def test_quick_check_invalid_json_raises():
    """generate_quick_check() must raise ValueError if OpenAI returns invalid JSON."""
    bad_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content="not valid json"))]
    )

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create.return_value = bad_response
        with pytest.raises(ValueError):
            generate_quick_check("German Articles", "A1")
