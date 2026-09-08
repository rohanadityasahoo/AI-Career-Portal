import re
import random


# ============================================================
# INTERVIEW QUESTION BANK
# ============================================================

INTERVIEW_QUESTIONS = {

    # --------------------------------------------------------
    # INFORMATION TECHNOLOGY
    # --------------------------------------------------------

    "Information Technology": {

        "technical": [
            "Explain one technical project you have worked on.",
            "Which programming language are you most comfortable with and why?",
            "How do you approach debugging a program when it is not working as expected?",
            "Explain the difference between a database and a programming language.",
            "What is the importance of version control in software development?",
            "How do you ensure that your code is maintainable and readable?",
            "Explain an API and give an example of how you have used one.",
            "What challenges have you faced while developing a software project?",
            "How do you learn a new programming language or technology?",
            "Explain a technical problem you solved and how you solved it."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Computer Science or Information Technology?",
            "What are your biggest strengths?",
            "What is one weakness you are currently working on?",
            "Where do you see yourself in the next five years?",
            "Tell me about a time when you worked as part of a team.",
            "How do you handle pressure and deadlines?",
            "Why should we consider you for this position?"
        ]
    },


    # --------------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------------

    "Electrical Engineering": {

        "technical": [
            "Explain Ohm's Law and its practical application.",
            "What is the difference between AC and DC?",
            "Explain the working principle of a transformer.",
            "What is power factor and why is it important?",
            "Explain the difference between a motor and a generator.",
            "What are the different types of electrical protection systems?",
            "What is the purpose of MATLAB or Simulink in electrical engineering?",
            "Explain the working principle of a three-phase system.",
            "What is a circuit breaker and why is it used?",
            "Describe an electrical engineering project you have worked on."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Electrical Engineering?",
            "What are your strongest technical skills?",
            "Tell me about a challenging engineering problem you solved.",
            "How do you work with a team?",
            "How do you handle deadlines?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # ELECTRONICS
    # --------------------------------------------------------

    "Electronics Engineering": {

        "technical": [
            "Explain the difference between analog and digital signals.",
            "What is a microcontroller?",
            "What is the difference between a microprocessor and a microcontroller?",
            "Explain the working principle of a diode.",
            "What is a transistor and where is it used?",
            "What is an embedded system?",
            "Explain a project involving Arduino, Raspberry Pi, or another microcontroller.",
            "What is PCB design?",
            "What is the difference between UART, SPI, and I2C?",
            "Explain a technical electronics problem you have solved."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Electronics Engineering?",
            "What electronics project are you most proud of?",
            "What are your strongest technical skills?",
            "Tell me about a difficult problem you solved.",
            "How do you handle teamwork?",
            "What are your career goals?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # CIVIL
    # --------------------------------------------------------

    "Civil Engineering": {

        "technical": [
            "Explain the difference between a beam and a column.",
            "What is the purpose of reinforcement in concrete?",
            "What is the difference between cement and concrete?",
            "Explain the basic principles of structural analysis.",
            "What is AutoCAD used for in civil engineering?",
            "What is STAAD Pro and where is it used?",
            "Explain the importance of surveying in construction.",
            "What are the different types of foundations?",
            "Explain a civil engineering project you have worked on.",
            "Describe a construction problem you have encountered and how you solved it."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Civil Engineering?",
            "What civil engineering project are you most proud of?",
            "What are your strongest technical skills?",
            "How do you handle pressure on a construction project?",
            "Tell me about a time you worked in a team.",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # MECHANICAL
    # --------------------------------------------------------

    "Mechanical Engineering": {

        "technical": [
            "Explain the first law of thermodynamics.",
            "What is the difference between heat and temperature?",
            "Explain the working principle of an internal combustion engine.",
            "What is CAD and why is it important?",
            "What is the purpose of SolidWorks or CATIA?",
            "Explain the difference between stress and strain.",
            "What is manufacturing process planning?",
            "Explain the working principle of a centrifugal pump.",
            "Describe a mechanical engineering project you have worked on.",
            "Explain a mechanical problem you solved."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Mechanical Engineering?",
            "Which mechanical engineering subject interests you most?",
            "Tell me about your best project.",
            "What are your strongest technical skills?",
            "How do you handle difficult engineering problems?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # MICROBIOLOGY
    # --------------------------------------------------------

    "Microbiology": {

        "technical": [
            "What is microbiology and what are its major branches?",
            "Explain the difference between bacteria and viruses.",
            "What is the purpose of Gram staining?",
            "Explain the difference between Gram-positive and Gram-negative bacteria.",
            "What is a culture medium?",
            "Explain the principle of sterilization.",
            "What is PCR and where is it used?",
            "What is the difference between aseptic and sterile techniques?",
            "Describe a microbiology laboratory project you have worked on.",
            "Explain a laboratory problem you encountered and how you solved it."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Microbiology?",
            "Which area of microbiology interests you most?",
            "Tell me about your laboratory experience.",
            "What are your strongest skills?",
            "How do you maintain accuracy during laboratory work?",
            "How do you handle mistakes in laboratory procedures?",
            "Where do you see yourself in five years?"
        ]
    },


    # --------------------------------------------------------
    # BIOTECHNOLOGY
    # --------------------------------------------------------

    "Biotechnology": {

        "technical": [
            "What is biotechnology?",
            "Explain recombinant DNA technology.",
            "What is PCR?",
            "Explain the difference between DNA and RNA.",
            "What is genetic engineering?",
            "What is cell culture?",
            "Explain the applications of biotechnology in healthcare.",
            "What is bioinformatics?",
            "Describe a biotechnology project you have worked on.",
            "What laboratory techniques are you familiar with?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Biotechnology?",
            "What area of biotechnology interests you most?",
            "Tell me about your research or laboratory experience.",
            "What are your strengths?",
            "How do you handle experimental failure?",
            "What are your career goals?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # PHARMACY
    # --------------------------------------------------------

    "Pharmacy": {

        "technical": [
            "What is pharmacology?",
            "Explain the difference between a drug and a medicine.",
            "What is pharmacokinetics?",
            "What is pharmacodynamics?",
            "Explain the different routes of drug administration.",
            "What factors affect drug absorption?",
            "What is drug interaction?",
            "What is the importance of dosage?",
            "Describe your pharmacy-related project or practical experience.",
            "What precautions should be followed when handling medicines?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Pharmacy?",
            "Which area of pharmacy interests you most?",
            "Tell me about your practical or laboratory experience.",
            "What are your strengths?",
            "How do you handle responsibility?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # HEALTHCARE
    # --------------------------------------------------------

    "Healthcare": {

        "technical": [
            "What are the most important principles of patient care?",
            "How do you maintain patient confidentiality?",
            "What is the importance of accurate documentation?",
            "How do you handle a medical emergency?",
            "What is infection control?",
            "Why is communication important in healthcare?",
            "How do you prioritize multiple patients or tasks?",
            "How do you ensure accuracy in your work?",
            "Describe your healthcare-related practical experience.",
            "Tell me about a challenging situation you handled."
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose healthcare?",
            "What are your strengths?",
            "How do you handle stressful situations?",
            "How do you communicate with patients?",
            "Tell me about a time you worked in a team.",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # FINANCE
    # --------------------------------------------------------

    "Finance & Accounting": {

        "technical": [
            "What is the difference between assets and liabilities?",
            "Explain the basic accounting equation.",
            "What is a balance sheet?",
            "What is a profit and loss statement?",
            "Explain cash flow.",
            "What is financial analysis?",
            "What is the difference between revenue and profit?",
            "What is the purpose of budgeting?",
            "Describe a finance or accounting project you have worked on.",
            "How would you identify an error in financial records?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Finance or Accounting?",
            "What are your strongest analytical skills?",
            "Tell me about a challenging financial problem you solved.",
            "How do you handle confidential information?",
            "How do you manage deadlines?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    "Marketing & Sales": {

        "technical": [
            "What is digital marketing?",
            "Explain the difference between SEO and SEM.",
            "What is a target audience?",
            "What is market segmentation?",
            "What is a marketing funnel?",
            "How would you measure the success of a marketing campaign?",
            "What is customer relationship management?",
            "Explain the importance of social media marketing.",
            "Describe a marketing project you have worked on.",
            "How would you improve a product's marketing strategy?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Marketing?",
            "What makes you interested in sales?",
            "How do you handle rejection?",
            "Tell me about a time you persuaded someone.",
            "What are your strengths?",
            "How do you work under targets?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # TRAVEL & TOURISM
    # --------------------------------------------------------

    "Travel & Tourism": {

        "technical": [
            "What are the key responsibilities of a travel consultant?",
            "How would you create an itinerary for a customer?",
            "What factors do you consider when recommending a destination?",
            "Explain the difference between domestic and international travel planning.",
            "How do airline and hotel reservations typically work?",
            "How would you handle a customer whose flight has been cancelled?",
            "What is destination management?",
            "How would you handle a customer complaint?",
            "Describe your travel or tourism experience.",
            "How do you ensure that a travel itinerary meets a customer's requirements?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Travel and Tourism?",
            "What do you enjoy most about working with customers?",
            "Tell me about a difficult customer you handled.",
            "How do you handle pressure during busy travel periods?",
            "What are your strongest communication skills?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # HOSPITALITY
    # --------------------------------------------------------

    "Hospitality & Hotel Management": {

        "technical": [
            "What are the major departments in a hotel?",
            "What are the responsibilities of the front office department?",
            "How does hotel reservation management work?",
            "How would you handle an unhappy hotel guest?",
            "What is guest relationship management?",
            "Explain the importance of housekeeping operations.",
            "What is food and beverage management?",
            "How would you handle an overbooking situation?",
            "Describe your hospitality experience.",
            "What makes good customer service in the hospitality industry?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Hospitality?",
            "How do you handle difficult guests?",
            "What does excellent customer service mean to you?",
            "How do you work during high-pressure situations?",
            "Tell me about a time you solved a customer problem.",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    },


    # --------------------------------------------------------
    # HUMAN RESOURCES
    # --------------------------------------------------------

    "Human Resources": {

        "technical": [
            "What are the major functions of Human Resources?",
            "Explain the recruitment and selection process.",
            "What is employee onboarding?",
            "What is performance management?",
            "How would you handle an employee conflict?",
            "What is employee engagement?",
            "Why is confidentiality important in HR?",
            "What is workforce planning?",
            "Describe an HR-related project you have worked on.",
            "How would you improve employee retention?"
        ],

        "hr": [
            "Tell me about yourself.",
            "Why did you choose Human Resources?",
            "What are your communication strengths?",
            "How do you handle conflicts between employees?",
            "Tell me about a time you worked with different types of people.",
            "How do you handle confidential information?",
            "Where do you see yourself in five years?",
            "Why should we hire you?"
        ]
    }
}


# ============================================================
# DEFAULT QUESTIONS
# ============================================================

DEFAULT_QUESTIONS = {

    "technical": [
        "Tell me about a project or practical experience mentioned in your resume.",
        "What is your strongest professional skill?",
        "What technical or domain-specific skill are you currently improving?",
        "Describe a difficult problem you solved.",
        "How do you keep yourself updated in your field?"
    ],

    "hr": [
        "Tell me about yourself.",
        "What are your greatest strengths?",
        "What is one weakness you are working to improve?",
        "Where do you see yourself in five years?",
        "Why should we hire you?"
    ]
}


# ============================================================
# NORMALIZE DOMAIN
# ============================================================

def normalize_domain(domain):

    if not domain:
        return "General"

    domain = str(domain).strip()

    aliases = {

        "IT":
            "Information Technology",

        "Computer Science":
            "Information Technology",

        "Computer Engineering":
            "Information Technology",

        "Electrical":
            "Electrical Engineering",

        "Electronics":
            "Electronics Engineering",

        "Civil":
            "Civil Engineering",

        "Mechanical":
            "Mechanical Engineering",

        "Finance":
            "Finance & Accounting",

        "Accounting":
            "Finance & Accounting",

        "Marketing":
            "Marketing & Sales",

        "HR":
            "Human Resources",

        "Tourism":
            "Travel & Tourism",

        "Hospitality":
            "Hospitality & Hotel Management"
    }

    return aliases.get(domain, domain)


# ============================================================
# RESUME SKILL QUESTIONS
# ============================================================

def generate_skill_questions(skills, limit=3):

    if not skills:
        return []

    questions = []

    skills = list(dict.fromkeys(skills))

    for skill in skills[:limit]:

        questions.append(
            f"You have mentioned {skill} in your resume. "
            f"How have you used {skill} in your academic, "
            f"professional, or practical experience?"
        )

    return questions


# ============================================================
# PROJECT QUESTIONS
# ============================================================

def generate_resume_questions(resume_text):

    if not resume_text:
        return []

    text = resume_text.lower()

    questions = []

    project_keywords = [
        "project",
        "developed",
        "implemented",
        "designed",
        "built",
        "research"
    ]

    if any(keyword in text for keyword in project_keywords):

        questions.append(
            "Can you explain one of the projects or practical experiences "
            "mentioned in your resume?"
        )

        questions.append(
            "What was your specific contribution to that project?"
        )

        questions.append(
            "What was the biggest challenge you faced during that project?"
        )

    return questions


# ============================================================
# GENERATE INTERVIEW
# ============================================================

def generate_interview_questions(
    resume_text,
    career_domain,
    skills=None,
    number_of_questions=10
):

    if not resume_text or not resume_text.strip():
        return []

    domain = normalize_domain(career_domain)

    skills = skills or []

    question_pool = INTERVIEW_QUESTIONS.get(
        domain,
        DEFAULT_QUESTIONS
    )

    questions = []

    # --------------------------------------------------------
    # Add resume/project questions
    # --------------------------------------------------------

    resume_questions = generate_resume_questions(
        resume_text
    )

    questions.extend(resume_questions[:2])

    # --------------------------------------------------------
    # Add skill-specific questions
    # --------------------------------------------------------

    skill_questions = generate_skill_questions(
        skills,
        limit=3
    )

    questions.extend(skill_questions)

    # --------------------------------------------------------
    # Add technical questions
    # --------------------------------------------------------

    technical_questions = list(
        question_pool.get(
            "technical",
            DEFAULT_QUESTIONS["technical"]
        )
    )

    random.shuffle(
        technical_questions
    )

    questions.extend(
        technical_questions
    )

    # --------------------------------------------------------
    # Add HR questions
    # --------------------------------------------------------

    hr_questions = list(
        question_pool.get(
            "hr",
            DEFAULT_QUESTIONS["hr"]
        )
    )

    random.shuffle(
        hr_questions
    )

    questions.extend(
        hr_questions
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique_questions = []

    seen = set()

    for question in questions:

        key = question.strip().lower()

        if key not in seen:

            seen.add(key)

            unique_questions.append(
                question
            )

    # --------------------------------------------------------
    # Return requested number
    # --------------------------------------------------------

    return unique_questions[
        :number_of_questions
    ]


# ============================================================
# INTERVIEW COMPATIBILITY / SESSION HELPERS
# ============================================================

ROLE_TO_DOMAIN = {
    "python_developer": "Information Technology",
    "software_engineer": "Information Technology",
    "backend_developer": "Information Technology",
    "frontend_developer": "Information Technology",
    "web_developer": "Information Technology",
    "data_scientist": "Information Technology",
    "data_analyst": "Information Technology",
    "ai_ml_engineer": "Information Technology",
    "cybersecurity": "Information Technology",
    "electrical_engineer": "Electrical Engineering",
    "electronics_engineer": "Electronics Engineering",
    "civil_engineer": "Civil Engineering",
    "mechanical_engineer": "Mechanical Engineering",
    "microbiologist": "Microbiology",
    "biotechnologist": "Biotechnology",
    "pharmacist": "Pharmacy",
    "healthcare": "Healthcare",
    "finance_accounting": "Finance & Accounting",
    "marketing_sales": "Marketing & Sales",
    "hr": "Human Resources",
    "travel_tourism": "Travel & Tourism",
    "hospitality": "Hospitality & Hotel Management",
}

# Difficulty controls the type/depth of questions.
# The question bank remains the source of the actual questions.
DIFFICULTY_SETTINGS = {
    "easy": {
        "technical_count": 1,
        "hr_count": 2,
    },
    "medium": {
        "technical_count": 2,
        "hr_count": 1,
    },
    "hard": {
        "technical_count": 3,
        "hr_count": 1,
    },
}


def normalize_role(role):
    """Convert the role used by the HTML form into a question-bank domain."""
    if not role:
        return "General"

    role_key = str(role).strip().lower()

    if role_key in ROLE_TO_DOMAIN:
        return ROLE_TO_DOMAIN[role_key]

    # Also accept already-normalized domain names.
    return normalize_domain(role)


def _display_role(role):
    return str(role or "your chosen role").replace("_", " ").title()


def _role_specific_prompts(role):
    """Create realistic prompts that make the interview specific to the role."""
    role_label = _display_role(role)

    return [
        (
            f"Describe a {role_label} project or practical assignment you "
            "completed. What was the goal, what did you personally own, "
            "which tools or methods did you use, and what was the result?"
        ),
        (
            f"Imagine an important {role_label} task is not producing the "
            "expected result. How would you investigate the issue, decide "
            "on a solution, and confirm that the solution worked?"
        ),
        (
            f"A high-priority {role_label} deliverable is at risk close to "
            "a deadline. How would you prioritise the work, communicate "
            "the risk, and protect the quality of the final outcome?"
        )
    ]


def _unique_questions(questions, fallback_questions, total=5):
    """Keep each interview session to distinct questions without losing length."""
    selected = []
    seen = set()

    for question in questions + fallback_questions:
        key = question.strip().lower()
        if key in seen:
            continue

        seen.add(key)
        selected.append(question)

        if len(selected) == total:
            break

    return selected


def get_question_pool(role, difficulty="medium", domain=None):
    """
    Build a balanced five-question interview for the selected role.

    The optional domain keeps this compatible with the wider role mapping in
    ``routes/interview.py`` while allowing role-specific scenario prompts.
    """
    domain = domain or normalize_role(role)

    question_bank = INTERVIEW_QUESTIONS.get(
        domain,
        DEFAULT_QUESTIONS
    )

    difficulty = str(difficulty or "medium").lower()

    if difficulty not in DIFFICULTY_SETTINGS:
        difficulty = "medium"

    technical = list(
        question_bank.get(
            "technical",
            DEFAULT_QUESTIONS["technical"]
        )
    )

    hr = list(
        question_bank.get(
            "hr",
            DEFAULT_QUESTIONS["hr"]
        )
    )

    random.shuffle(technical)
    random.shuffle(hr)

    role_prompts = _role_specific_prompts(role)

    # Each difficulty uses a deliberate mix instead of merely taking the
    # first available questions from a shuffled list.
    if difficulty == "easy":
        selected = [
            hr[0],
            role_prompts[0],
            technical[0],
            hr[1],
            role_prompts[1]
        ]
    elif difficulty == "hard":
        selected = [
            technical[0],
            technical[1],
            role_prompts[2],
            technical[2],
            hr[0]
        ]
    else:
        selected = [
            technical[0],
            role_prompts[0],
            technical[1],
            role_prompts[1],
            hr[0]
        ]

    return _unique_questions(selected, technical + hr, total=5)


def generate_question(role, difficulty="medium"):
    """Generate one question for the current interview session."""
    pool = get_question_pool(role, difficulty)

    if not pool:
        return None

    return random.choice(pool)


QUESTION_STOP_WORDS = {
    "about", "after", "before", "could", "does", "explain", "from",
    "have", "into", "most", "should", "tell", "that", "their", "them",
    "then", "this", "what", "when", "where", "which", "while", "with",
    "would", "your", "yourself"
}

ACTION_WORDS = {
    "analyzed", "built", "created", "debugged", "delivered", "designed",
    "developed", "implemented", "improved", "led", "managed", "measured",
    "organized", "resolved", "solved", "tested", "worked"
}

REASONING_CUES = {
    "because", "therefore", "however", "approach", "process", "reason",
    "first", "then", "finally", "so", "while", "whereas"
}

EVIDENCE_CUES = {
    "for example", "for instance", "in my project", "in my experience",
    "i built", "i created", "i developed", "i implemented", "i worked",
    "result", "impact", "increased", "improved", "reduced", "saved"
}

STAR_CUES = {
    "situation", "task", "action", "result", "challenge", "outcome",
    "responsibility", "goal"
}

FILLER_RESPONSES = {
    "yes", "no", "okay", "good", "fine", "maybe", "nothing", "dont",
    "don't", "idk", "i dont know", "i don't know", "not sure"
}


def _tokenize(text):
    return re.findall(r"\b[\w+#.-]+\b", str(text).lower())


def _contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def _question_keywords(question):
    return {
        word for word in _tokenize(question)
        if len(word) >= 4 and word not in QUESTION_STOP_WORDS
    }


def _is_experience_question(question):
    prompt = str(question or "").lower()
    return any(
        phrase in prompt
        for phrase in [
            "tell me about", "describe", "project", "experience",
            "time when", "challenge", "worked", "handled", "solved"
        ]
    )


def _score_answer_rubric(answer, question=None):
    """Score an answer against a consistent interview-practice rubric."""
    text = str(answer).strip()
    lower = text.lower()
    words = _tokenize(text)
    word_count = len(words)

    if not words:
        return {
            "Relevance": 0,
            "Depth": 0,
            "Evidence": 0,
            "Structure": 0,
            "Clarity": 0,
            "score": 0
        }

    if lower in FILLER_RESPONSES:
        return {
            "Relevance": 2,
            "Depth": 1,
            "Evidence": 0,
            "Structure": 1,
            "Clarity": 1,
            "score": 5
        }

    question_terms = _question_keywords(question)
    answer_terms = set(words)
    matched_terms = question_terms.intersection(answer_terms)
    experience_question = _is_experience_question(question)

    # Relevance (30): assess whether the response addresses this specific prompt.
    if question_terms:
        relevance = min(
            18,
            round(18 * len(matched_terms) / min(len(question_terms), 4))
        )
    else:
        relevance = 15

    if experience_question:
        if re.search(r"\b(i|my|we|our)\b", lower):
            relevance += 5
        if answer_terms.intersection(ACTION_WORDS):
            relevance += 5
    elif _contains_any(lower, {"is", "means", "because", "works", "used"}):
        relevance += 5

    if "difference" in str(question or "").lower() and _contains_any(
        lower, {"while", "whereas", "difference", "compared"}
    ):
        relevance += 4

    relevance = min(relevance, 30)

    # Depth (20): reward sufficient detail but cap the gain from verbosity.
    if word_count >= 100:
        depth = 20
    elif word_count >= 70:
        depth = 17
    elif word_count >= 45:
        depth = 14
    elif word_count >= 25:
        depth = 10
    elif word_count >= 12:
        depth = 6
    else:
        depth = 2

    # Evidence (20): examples, ownership, measurable impact, and concrete action.
    evidence = 0
    if _contains_any(lower, EVIDENCE_CUES):
        evidence += 7
    if re.search(r"\b\d+(?:\.\d+)?(?:%|x)?\b", lower):
        evidence += 5
    if answer_terms.intersection(ACTION_WORDS):
        evidence += 4
    if _contains_any(lower, {"project", "team", "customer", "user", "client"}):
        evidence += 4
    evidence = min(evidence, 20)

    # Structure (20): look for a readable explanation or a STAR-style story.
    sentence_count = len([
        sentence for sentence in re.split(r"[.!?]+", text) if sentence.strip()
    ])
    structure = 0
    if sentence_count >= 2:
        structure += 4
    if sentence_count >= 3:
        structure += 2
    structure += min(7, len(answer_terms.intersection(REASONING_CUES)) * 2)
    structure += min(7, len(answer_terms.intersection(STAR_CUES)) * 2)
    structure = min(structure, 20)

    # Clarity (10): concise sentences and varied vocabulary are easier to follow.
    unique_ratio = len(set(words)) / word_count
    clarity = 2
    if unique_ratio >= 0.55:
        clarity += 4
    elif unique_ratio >= 0.4:
        clarity += 2
    if sentence_count >= 2:
        clarity += 2
    if not re.search(r"\b(umm+|uhh+|basically|whatever)\b", lower):
        clarity += 2
    clarity = min(clarity, 10)

    score = relevance + depth + evidence + structure + clarity

    # Long but off-topic answers should never receive an interview-ready score.
    if question_terms and relevance < 10 and word_count >= 20:
        score = min(score, 45)
    if word_count < 10:
        score = min(score, 25)
    if _contains_any(lower, {"i don't know", "not sure", "no idea"}):
        score = min(score, 20)

    return {
        "Relevance": relevance,
        "Depth": depth,
        "Evidence": evidence,
        "Structure": structure,
        "Clarity": clarity,
        "score": max(0, min(100, round(score)))
    }


def _answer_quality_score(answer):
    """Backward-compatible shortcut for callers that only need a score."""
    return _score_answer_rubric(answer)["score"]


def evaluate_answer(answer, question=None, role=None, difficulty=None):
    """
    Evaluate an interview answer.

    The existing route currently calls evaluate_answer_ai(answer), so
    `question`, `role`, and `difficulty` are optional for backward
    compatibility.

    Returns:
        {
            "score": int,
            "feedback": str,
            "strengths": list,
            "improvements": list
        }
    """
    if not answer or not str(answer).strip():
        return {
            "score": 0,
            "feedback": "No answer was provided.",
            "strengths": [],
            "improvements": ["Provide a complete answer to the question."]
        }

    text = str(answer).strip()
    rubric = _score_answer_rubric(text, question)
    score = rubric["score"]

    strengths = []
    improvements = []

    if rubric["Relevance"] >= 20:
        strengths.append("You addressed the main point of the question.")
    else:
        improvements.append("Answer the exact question first before adding background detail.")

    if rubric["Depth"] >= 14:
        strengths.append("Your answer contains useful supporting detail.")
    else:
        improvements.append("Add context and explain the steps behind your answer.")

    if rubric["Evidence"] >= 10:
        strengths.append("You supported your answer with concrete evidence or experience.")
    else:
        improvements.append("Include a specific example, action you took, or measurable result.")

    if rubric["Structure"] >= 10:
        strengths.append("Your answer has a clear, easy-to-follow structure.")
    else:
        improvements.append("Use a simple structure: situation, action, and result—or claim, reason, and example.")

    if rubric["Clarity"] < 6:
        improvements.append("Use short, complete sentences and avoid filler words.")

    strengths = strengths[:3]
    improvements = improvements[:3]

    if score >= 80:
        feedback = (
            "Strong answer. You provided useful detail and demonstrated "
            "good explanation or practical understanding."
        )
    elif score >= 60:
        feedback = (
            "Good answer. The main idea is understandable, but adding "
            "more detail, reasoning, or a practical example would make it stronger."
        )
    elif score >= 40:
        feedback = (
            "Average answer. Try to explain your reasoning more clearly "
            "and support your response with a specific example."
        )
    else:
        feedback = (
            "The answer needs improvement. Give a direct response, explain "
            "your reasoning, and include a relevant example or experience."
        )

    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
        "rubric": {
            name: value
            for name, value in rubric.items()
            if name != "score"
        }
    }
