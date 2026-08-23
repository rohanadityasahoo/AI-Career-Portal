"""Transparent rule-based guidance for the CareerPilot chatbot.

The chatbot does not call an external AI model or API. It matches career
topics in a student's question and returns curated, easy-to-explain advice.
"""


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


def get_response(message):
    """Return curated advice for one or more career topics in *message*."""

    cleaned_message = " ".join(str(message or "").lower().split())

    if not cleaned_message:
        return "Please type a career-related question so I can help."

    matched_responses = []

    for keywords, response in TOPIC_RESPONSES:
        if any(keyword in cleaned_message for keyword in keywords):
            matched_responses.append(response)

    if matched_responses:
        # Returning up to two focused answers keeps multi-topic replies useful
        # without making the page difficult to read.
        return "\n\n".join(matched_responses[:2])

    return (
        "I can help with careers, resumes, interviews, skills, projects, "
        "internships, placements, and job preparation. Try asking about one "
        "of these topics."
    )
