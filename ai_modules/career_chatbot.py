"""Transparent rule-based guidance for the CareerPilot chatbot.

The chatbot does not call an external AI model or API. It matches career
topics in a student's question and returns curated, easy-to-explain advice.
"""

import re


TOPIC_RESPONSES = [
    (
        ("hello", "hi", "hey"),
        "Hello! I can help you with careers, resumes, interviews, skills, "
        "projects, internships, placements, and job preparation."
    ),
    (
        ("resume", "cv", "ats"),
        "Resume tips: use a clear one-page layout, add role-relevant skills, "
        "describe projects with outcomes, and use keywords from the job role."
    ),
    (
        ("interview", "mock interview", "hr question"),
        "Interview tips: practise explaining your projects, use the STAR "
        "method for experience questions, and support answers with examples."
    ),
    (
        ("python", "programming", "coding", "developer"),
        "Technical-skills tip: build small projects regularly, practise core "
        "concepts, and keep your code in a portfolio you can explain."
    ),
    (
        ("skill", "learn", "course", "certification"),
        "Skills tip: choose one target role, list its common skills, then make "
        "a weekly learning plan with practice tasks and one portfolio project."
    ),
    (
        ("roadmap", "career path", "path"),
        "Career-roadmap tip: start with fundamentals, build projects, prepare "
        "your resume, practise interviews, and apply for relevant opportunities."
    ),
    (
        ("job", "role", "career"),
        "Career guidance: compare roles by required skills, daily work, growth "
        "opportunities, and your interests before choosing a target role."
    ),
    (
        ("internship", "intern"),
        "Internship tip: apply early, tailor your resume, show 2–3 relevant "
        "projects, and clearly explain what you learned from each project."
    ),
    (
        ("placement", "campus drive", "campus placement"),
        "Placement preparation: revise aptitude and core subjects, complete your "
        "resume, practise interviews, and take part in mock placement drives."
    ),
    (
        ("project", "portfolio", "github"),
        "Project tip: choose a practical problem, document your contribution, "
        "show the technologies used, and explain the result or learning outcome."
    ),
    (
        ("linkedin", "network", "networking"),
        "Professional-profile tip: keep LinkedIn updated with your skills, "
        "projects, education, and a short headline for your target role."
    ),
]


FOLLOW_UP_PHRASES = (
    "what next",
    "next step",
    "what should i do next",
    "tell me more",
    "more details",
    "how do i start",
)


def _contains_keyword(message, keyword):
    """Match a complete word or phrase instead of a partial word."""

    return bool(
        re.search(
            rf"\b{re.escape(keyword)}\b",
            message
        )
    )


def _matched_responses(message):
    """Return the curated responses matching *message*."""

    return [
        response
        for keywords, response in TOPIC_RESPONSES
        if any(_contains_keyword(message, keyword) for keyword in keywords)
    ]


def _is_follow_up(message):
    """Identify common short follow-up questions."""

    return (
        message in {"next", "more", "continue"}
        or any(phrase in message for phrase in FOLLOW_UP_PHRASES)
    )


def _profile_note(student_context):
    """Create a short, optional personalization note from the student profile."""

    if not student_context:
        return ""

    target_role = str(
        student_context.get('target_role') or ''
    ).strip()

    if not target_role:
        return ""

    formatted_role = target_role.replace('_', ' ').title()

    return f"Personalized for your target role: {formatted_role}.\n\n"


def get_response(message, student_context=None, previous_question=None):
    """Return curated guidance, with optional profile and follow-up context."""

    cleaned_message = " ".join(str(message or "").lower().split())

    if not cleaned_message:
        return "Please type a career-related question so I can help."

    matched_responses = _matched_responses(cleaned_message)
    follow_up_prefix = ""

    if (
        not matched_responses
        and previous_question
        and _is_follow_up(cleaned_message)
    ):
        previous_message = " ".join(
            str(previous_question).lower().split()
        )
        matched_responses = _matched_responses(previous_message)[:1]
        follow_up_prefix = (
            "Based on your previous question, here is a useful next step:\n\n"
        )

    if matched_responses:
        # Returning up to two focused answers keeps multi-topic replies useful
        # without making the page difficult to read.
        return (
            _profile_note(student_context)
            + follow_up_prefix
            + "\n\n".join(matched_responses[:2])
        )

    return (
        "I can help with careers, resumes, interviews, skills, projects, "
        "internships, placements, and job preparation. Try asking about one "
        "of these topics."
    )
