import gc
import re
from ai_modules.ai_resume_analyzer import encode_texts

# ============================================================
# EXPANDED KNOWLEDGE BASE
# ============================================================

TOPIC_RESPONSES = [
    (
        ("hello", "hi", "hey", "greetings"),
        (
            "Hello! I am your CareerPilot AI assistant. I can guide you on"
            " resumes, mock interviews, skills roadmaps, projects, internships,"
            " campus placements, and job preparation. What would you like help"
            " with?"
        ),
        "greeting and introduction",
    ),
    (
        ("resume", "cv", "ats", "format", "one page"),
        (
            "Resume Best Practices:\n• Keep it strictly to 1 page for students"
            " and freshers.\n• Use clear section headings: Education, Skills,"
            " Projects, Experience/Training.\n• Include measurable impact"
            " (e.g., 'Reduced inspection time by 30% using QR tracking').\n•"
            " Incorporate exact keywords from the target job description to pass"
            " ATS filters."
        ),
        "resume writing formatting ats score keywords",
    ),
    (
        (
            "interview",
            "mock interview",
            "hr question",
            "behavioral",
            "star method",
            "tell me about yourself",
        ),
        (
            "Interview Preparation Tips:\n• Use the STAR method (Situation,"
            " Task, Action, Result) for situational and behavioral questions.\n•"
            " Structure 'Tell me about yourself' as: Past (education/training)"
            " -> Present (current projects/skills) -> Future (why this role).\n•"
            " Be prepared to explain every single technology and library listed"
            " on your resume in depth."
        ),
        "interview tips mock interview hr questions behavioral star method",
    ),
    (
        (
            "coding",
            "programming",
            "python",
            "java",
            "dsa",
            "data structures",
            "algorithms",
            "leetcode",
        ),
        (
            "Technical & Coding Guidance:\n• Focus on core Data Structures"
            " (Arrays, Strings, HashMaps, Trees, Graphs, Two Pointers).\n•"
            " Practice 2–3 problems daily on LeetCode or HackerRank rather than"
            " cramming.\n• Always write readable, clean code and practice"
            " explaining your time and space complexity (Big-O)."
        ),
        "coding programming dsa data structures algorithms leetcode",
    ),
    (
        ("skill", "learn", "course", "certification", "upskill"),
        (
            "Upskilling Strategy:\n• Identify 3–5 non-negotiable skills for"
            " your target role from job postings.\n• Pair theoretical learning"
            " (Coursera/Udemy/docs) immediately with a hands-on project.\n•"
            " Aim for depth in one primary tech stack (e.g., Python + Flask +"
            " SQL) before jumping to another framework."
        ),
        "learning skills upskilling courses certifications",
    ),
    (
        ("roadmap", "career path", "path", "how to become", "guide"),
        (
            "Career Roadmap Strategy:\n• Step 1: Core Fundamentals &"
            " Logic.\n• Step 2: Frameworks, Databases & Tooling.\n• Step 3:"
            " Real-world Projects & Version Control (Git/GitHub).\n• Step 4:"
            " ATS Resume & Portfolio Deployment.\n• Step 5: Mock Interviews &"
            " Targeted Job Applications.\nCheck the 'Career Roadmap' tab in"
            " your portal for a role-specific breakdown!"
        ),
        "career roadmap learning path step by step guide",
    ),
    (
        ("internship", "intern", "summer training"),
        (
            "Internship Search Strategy:\n• Start applying 3–6 months in"
            " advance.\n• Customize your resume summary and skills for each"
            " company.\n• Reach out directly to alumni and hiring managers on"
            " LinkedIn with a concise, polite cold pitch.\n• Highlight"
            " hands-on project contributions and real-world problem solving."
        ),
        "internships finding intern training summer internship",
    ),
    (
        ("placement", "campus drive", "aptitude", "campus placement"),
        (
            "Campus Placement Strategy:\n• Quantitative & Verbal Aptitude: Daily"
            " 30-minute practice tests.\n• Core CS Fundamentals: Revise DBMS,"
            " OS, Computer Networks, and OOP.\n• Resume Verification: Double-check"
            " that your project repo links and GitHub are active and"
            " presentable."
        ),
        "campus placements placement drive aptitude test core subjects",
    ),
    (
        ("project", "portfolio", "github", "open source"),
        (
            "Portfolio & Project Tips:\n• Build solutions for real problems"
            " rather than generic clones (e.g., todo lists).\n• Include a clean"
            " README with screenshots, architecture diagrams, and live demo"
            " links.\n• Document the challenges you faced and how you solved"
            " them."
        ),
        "building projects portfolio github repositories open source",
    ),
    (
        ("linkedin", "network", "networking", "connections"),
        (
            "Networking & LinkedIn Tips:\n• Keep a professional headline (e.g.,"
            " 'Aspiring Backend Developer | Python, Flask, MySQL | KIIT').\n•"
            " Post brief project milestones and what you learned.\n• Connect"
            " with alumni and professionals working in your target companies"
            " with personalized notes."
        ),
        "linkedin profile professional networking connecting with recruiters",
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
  """Match complete words/phrases instead of partial strings."""
  return bool(re.search(rf"\b{re.escape(keyword)}\b", message))


def _matched_keyword_responses(message):
  """Returns curated responses matching keywords in the message."""
  return [
      response
      for keywords, response, _ in TOPIC_RESPONSES
      if any(_contains_keyword(message, keyword) for keyword in keywords)
  ]


def _semantic_fallback(message):
  """Uses the shared embedding model to semantically find the most relevant response."""
  try:
    descriptions = [desc for _, _, desc in TOPIC_RESPONSES]
    all_texts = [message] + descriptions

    embeddings = encode_texts(all_texts)
    if len(embeddings) < 2:
      return None

    query_emb = embeddings[0]
    topic_embs = embeddings[1:]

    # Cosine similarities
    similarities = topic_embs @ query_emb
    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx])

    # Clean up memory
    del embeddings, query_emb, topic_embs
    gc.collect()

    # If confidence is above 0.35, return the matched guidance
    if best_score >= 0.35:
      return TOPIC_RESPONSES[best_idx][1]
  except Exception:
    pass

  return None


def _is_follow_up(message):
  return message in {"next", "more", "continue"} or any(
      phrase in message for phrase in FOLLOW_UP_PHRASES
  )


def _profile_note(student_context):
  if not student_context:
    return ""
  target_role = str(student_context.get("target_role") or "").strip()
  if not target_role:
    return ""
  formatted_role = target_role.replace("_", " ").title()
  return f"Personalized for your target role: {formatted_role}.\n\n"


# ============================================================
# MAIN ENTRYPOINT
# ============================================================


def get_response(message, student_context=None, previous_question=None):
  """Return curated guidance with keyword matching, semantic fallback, and follow-up context."""
  cleaned_message = " ".join(str(message or "").lower().split())

  if not cleaned_message:
    return (
        "Please type a career-related question so I can provide actionable"
        " guidance."
    )

  follow_up_prefix = ""

  # 1. Check for quick follow-up
  if previous_question and _is_follow_up(cleaned_message):
    prev_clean = " ".join(str(previous_question).lower().split())
    prev_matches = _matched_keyword_responses(prev_clean)
    if prev_matches:
      return (
          "Based on your previous question, here is the recommended next"
          f" step:\n\n{prev_matches[0]}"
      )

  # 2. Fast Keyword Matching
  matched_responses = _matched_keyword_responses(cleaned_message)

  if matched_responses:
    return (
        _profile_note(student_context)
        + follow_up_prefix
        + "\n\n".join(matched_responses[:2])
    )

  # 3. AI Semantic Embedding Match
  semantic_match = _semantic_fallback(cleaned_message)
  if semantic_match:
    return _profile_note(student_context) + semantic_match

  # 4. Graceful Fallback
  return (
      "I can help you with specific career topics. Try asking about:\n"
      "• **Resumes & ATS**: How to optimize layout and pass ATS filters\n"
      "• **Mock Interviews**: STAR method, HR, and technical questions\n"
      "• **Skills & Roadmaps**: Step-by-step learning paths for tech &"
      " engineering\n"
      "• **Projects & GitHub**: Building standout portfolio projects\n"
      "• **Internships & Placements**: Application strategies and aptitude prep"
  )