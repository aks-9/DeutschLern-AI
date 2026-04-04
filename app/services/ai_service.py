"""AI service — all OpenAI API calls are centralised here.

Never call the OpenAI API from routers, models, or templates.
"""

import json

from openai import OpenAI

from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_exercise(topic: str, level: str) -> dict:
    """Generate a fill-in-the-blank exercise for a grammar topic.

    :param topic: The grammar topic title, e.g. 'German Articles'.
    :param level: CEFR level string, e.g. 'A1'.
    :raises ValueError: If the API response is not valid JSON.
    :return: Dict with keys sentence, blank_word, hint, explanation.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini", # this model is cheap and fast, sufficient for exercises
        response_format={"type": "json_object"}, #forces OpenAI to return valid JSON
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a German language teacher creating exercises "
                    f"for CEFR {level} students. Always respond with "
                    f"valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create a fill-in-the-blank exercise for the grammar "
                    f"topic: '{topic}'.\n"
                    f"Return JSON with exactly these fields:\n"
                    f"- sentence: German sentence with ____ as the blank\n"
                    f"- blank_word: the correct word for the blank\n"
                    f"- hint: short English hint\n"
                    f"- explanation: one sentence explaining the answer"
                ),
            },
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e: #catches bad responses and raises ValueError
        raise ValueError(
            f"OpenAI returned invalid JSON: {e}"
        )


def grade_answer(
    sentence: str,
    blank_word: str,
    user_answer: str,
    level: str,
) -> dict:
    """Grade a user's answer to a fill-in-the-blank exercise.

    :param sentence: The exercise sentence with ____ as the blank.
    :param blank_word: The correct answer.
    :param user_answer: The answer submitted by the user.
    :param level: CEFR level string, e.g. 'A1'.
    :raises ValueError: If the API response is not valid JSON.
    :return: Dict with keys correct (bool), score (float), feedback (str).
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a German language teacher. "
                    "Respond with JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Grade this answer for a CEFR {level} "
                    f"fill-in-the-blank exercise.\n"
                    f"Sentence: {sentence}\n"
                    f"Correct answer: {blank_word}\n"
                    f"Student answer: {user_answer}\n"
                    f"Return JSON with exactly these fields:\n"
                    f"- correct: true or false\n"
                    f"- score: float between 0.0 and 1.0\n"
                    f"- feedback: one encouraging sentence"
                ),
            },
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"OpenAI returned invalid JSON: {e}"
        )


def generate_quick_check(topic: str, level: str) -> dict:
    """Generate a multiple-choice quick-check question for a grammar topic.

    :param topic: The grammar topic title, e.g. 'German Articles'.
    :param level: CEFR level string, e.g. 'A1'.
    :raises ValueError: If the API response is not valid JSON.
    :return: Dict with keys question, options (list of 4), correct_index, explanation.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a German language teacher creating "
                    f"multiple-choice questions for CEFR {level} students. "
                    f"Always respond with valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create a multiple-choice quick-check question for "
                    f"the grammar topic: '{topic}'.\n"
                    f"Return JSON with exactly these fields:\n"
                    f"- question: one clear question in English\n"
                    f"- options: list of exactly 4 short answer strings\n"
                    f"- correct_index: integer 0-3 pointing to the correct option\n"
                    f"- explanation: one sentence explaining the correct answer"
                ),
            },
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"OpenAI returned invalid JSON: {e}"
        )
