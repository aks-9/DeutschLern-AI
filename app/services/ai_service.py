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
                    f"- feedback: one encouraging sentence in German\n"
                    f"- feedback_en: English translation of the feedback"
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


def generate_example_sentence(word: str, level: str) -> str:
    """Generate one natural German example sentence using the given word.

    :param word: The German word or phrase to use in the sentence.
    :param level: CEFR level string, e.g. 'A1'. Determines sentence complexity.
    :return: A single German sentence as a plain string.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=80, # limiting tokens to save cost as we just need 1 short sentence.
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a German teacher for CEFR {level} learners. "
                    f"Write natural, level-appropriate sentences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Write ONE natural German example sentence using the word '{word}'. "
                    f"The sentence must be appropriate for {level} level. "
                    f"Reply with only the German sentence, nothing else."
                ),
            },
        ],
    )
    return response.choices[0].message.content.strip() # strip() removes any trailing newline or a leading space from GPT response. Because we don't expect JSON but plain text.


# ── Conversation Coach ────────────────────────────────────────────────────────

SCENARIO_PROMPTS = {
    "free":        "The student wants a free conversation on any topic.",
    "supermarket": "You are roleplaying: the student is shopping at a German supermarket (REWE). Help them navigate buying groceries, asking prices, and finding items.",
    "train":       "You are roleplaying: the student is at Berlin Hauptbahnhof buying a train ticket. Help them with directions, platforms, and ticket vocabulary.",
    "interview":   "You are roleplaying: the student is in a casual German job interview at a Berlin startup. Keep it simple and encouraging for their level.",
}

LEVEL_INSTRUCTIONS = {
    "A1": "Use ONLY simple present tense. Maximum 2 short sentences per reply. After each reply, add an English translation in italics on a new line starting with '(Translation: ...)'",
    "A2": "Use present tense and Perfekt past tense. 2-3 sentences per reply. Occasionally use modal verbs. No English translation needed.",
    "B1": "Use varied grammar including subordinate clauses, Konjunktiv II where natural. 3-4 sentences per reply. Respond entirely in German.",
}


def build_coach_system_prompt(level: str, scenario: str) -> str:
    """Build the system prompt for the AI coach based on user level and scenario.

    :param level: CEFR level string, e.g. 'A1'.
    :param scenario: Scenario key, e.g. 'free', 'supermarket', 'train', 'interview'.
    :return: A fully formatted system prompt string ready to send to the API.
    """
    scenario_instruction = SCENARIO_PROMPTS.get(scenario, SCENARIO_PROMPTS["free"]) # falls back to "free" instead of crashing under unknown scenarios.
    level_instruction    = LEVEL_INSTRUCTIONS.get(level, LEVEL_INSTRUCTIONS["A1"])

    return f"""You are a friendly, encouraging German language coach for a CEFR {level} learner.

SCENARIO: {scenario_instruction}

LANGUAGE RULES FOR {level}:
{level_instruction}

CORRECTION RULE: If the student makes a grammar error, FIRST respond naturally to what they said, THEN on a new line add: " * Kleine Korrektur: '[their error]' → '[correction]' — [one-line explanation in English]"

IMPORTANT: Always stay in character. Be warm, patient, and encouraging."""


def get_coach_reply(history: list[dict], system_prompt: str) -> str:
    """Call GPT-4o with the full conversation history and return the coach's reply.

    :param history: List of {"role": ..., "content": ...} dicts, oldest first.
    :param system_prompt: The personalised system prompt from build_coach_system_prompt().
    :return: The coach's reply as a plain string.
    """
    messages = [{"role": "system", "content": system_prompt}] + history
    try:
        response = client.chat.completions.create(
            model="gpt-4o", #using the full model for better conversation quality
            max_tokens=400,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Entschuldigung, ich hatte ein technisches Problem. Bitte versuche es noch einmal. (Sorry, I had a technical problem. Please try again.)"
