"""Tests for ai_service.py — generate_exercise() and grade_answer()."""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_service import generate_exercise, grade_answer


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
