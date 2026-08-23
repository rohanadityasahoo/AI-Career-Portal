import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# AI MODEL
# =========================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =========================================================
# AI RESUME QUALITY CRITERIA
# =========================================================

CRITERIA = {

    "professional_summary": (
        "A professional resume containing a clear summary "
        "or profile describing the candidate's career background "
        "and professional strengths."
    ),

    "experience": (
        "A resume containing relevant work experience with "
        "job titles, organizations, responsibilities, and achievements."
    ),

    "skills": (
        "A resume clearly presenting relevant professional, "
        "technical, or domain-specific skills."
    ),

    "education": (
        "A resume containing clear educational qualifications, "
        "degrees, institutions, and academic information."
    ),

    "projects": (
        "A resume containing projects or practical work "
        "that demonstrate relevant abilities and experience."
    ),

    "achievements": (
        "A resume containing measurable achievements, awards, "
        "results, responsibilities, or demonstrated impact."
    ),

    "professional_language": (
        "A professional resume written using clear, concise, "
        "structured, and professional language."
    )

}


# =========================================================
# CAREER ROLE PROFILES
# =========================================================

ROLE_PROFILES = {

    "IT Project Manager": {

        "description": """
        information technology project management
        Agile Scrum Jira SDLC project planning
        scheduling budgeting stakeholders software projects
        """,

        "keywords": [
            "project management",
            "project manager",
            "agile",
            "scrum",
            "jira",
            "sdlc",
            "software project",
            "stakeholder",
            "budget",
            "scheduling"
        ]

    },


    "Software Engineer": {

        "description": """
        software engineering programming coding software development
        software applications algorithms technical implementation
        """,

        "keywords": [
            "software engineer",
            "software development",
            "programming",
            "python",
            "java",
            "javascript",
            "api",
            "restful",
            "django",
            "node.js"
        ]

    },


    "Backend Developer": {

        "description": """
        backend development server application programming
        APIs databases Python Java Django Flask Node.js
        """,

        "keywords": [
            "backend",
            "api",
            "restful api",
            "python",
            "django",
            "flask",
            "node.js",
            "database"
        ]

    },


    "Frontend Developer": {

        "description": """
        frontend web development HTML CSS JavaScript
        React Angular Vue user interface
        """,

        "keywords": [
            "frontend",
            "html",
            "css",
            "javascript",
            "react",
            "angular",
            "vue",
            "user interface"
        ]

    },


    "Data Analyst": {

        "description": """
        data analysis analytics SQL Python Excel statistics
        dashboards data visualization business intelligence
        """,

        "keywords": [
            "data analysis",
            "analytics",
            "sql",
            "excel",
            "statistics",
            "dashboard",
            "data visualization"
        ]

    },


    "Machine Learning Engineer": {

        "description": """
        machine learning artificial intelligence Python
        models algorithms data science deep learning
        """,

        "keywords": [
            "machine learning",
            "artificial intelligence",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "data science"
        ]

    },


    "Business Analyst": {

        "description": """
        business analysis requirements analysis stakeholders
        process improvement documentation business requirements
        """,

        "keywords": [
            "business analyst",
            "requirements",
            "stakeholder",
            "business requirements",
            "process improvement",
            "business analysis"
        ]

    },


    "Electrical Engineer": {

        "description": """
        electrical engineering power systems electrical machines
        MATLAB Simulink control systems PLC SCADA
        """,

        "keywords": [
            "electrical engineering",
            "matlab",
            "simulink",
            "plc",
            "scada",
            "power systems",
            "electrical machines"
        ]

    },


    "Electronics Engineer": {

        "description": """
        electronics engineering embedded systems
        microcontrollers Arduino PCB VLSI FPGA
        """,

        "keywords": [
            "electronics",
            "embedded systems",
            "microcontroller",
            "arduino",
            "pcb",
            "vlsi",
            "fpga"
        ]

    },


    "Civil Engineer": {

        "description": """
        civil engineering construction structural engineering
        AutoCAD STAAD Pro Revit surveying
        """,

        "keywords": [
            "civil engineering",
            "autocad",
            "staad pro",
            "revit",
            "structural engineering",
            "surveying",
            "construction"
        ]

    },


    "Mechanical Engineer": {

        "description": """
        mechanical engineering manufacturing CAD
        SolidWorks CATIA ANSYS thermodynamics
        """,

        "keywords": [
            "mechanical engineering",
            "solidworks",
            "catia",
            "ansys",
            "cad",
            "manufacturing",
            "thermodynamics"
        ]

    },


    "Travel Consultant": {

        "description": """
        travel tourism travel planning reservations
        itineraries destinations travel consulting
        customer service hospitality
        """,

        "keywords": [
            "travel consultant",
            "tourism",
            "travel planning",
            "reservations",
            "itineraries",
            "hospitality"
        ]

    }

}


# =========================================================
# SEMANTIC SCORE
# =========================================================

def semantic_score(resume_text, criterion):

    if not resume_text or not resume_text.strip():
        return 0.0

    resume_embedding = model.encode(
        [resume_text],
        normalize_embeddings=True
    )

    criterion_embedding = model.encode(
        [criterion],
        normalize_embeddings=True
    )

    similarity = cosine_similarity(
        resume_embedding,
        criterion_embedding
    )[0][0]

    score = (
        (similarity + 1) / 2
    ) * 100

    return round(
        max(
            0,
            min(
                100,
                float(score)
            )
        ),
        2
    )


# =========================================================
# AI RESUME QUALITY
# =========================================================

def calculate_ai_resume_quality(resume_text):

    if not resume_text or not resume_text.strip():
        return 0.0

    scores = []

    for criterion in CRITERIA.values():

        score = semantic_score(
            resume_text,
            criterion
        )

        scores.append(score)

    if not scores:
        return 0.0

    final_score = (
        sum(scores)
        / len(scores)
    )

    return round(
        final_score,
        2
    )


# =========================================================
# AI CAREER ROLE RECOMMENDATION
# =========================================================

def recommend_ai_roles(
    resume_text,
    top_n=5
):

    if not resume_text or not resume_text.strip():
        return []

    # -----------------------------------------------------
    # Normalize resume text
    # -----------------------------------------------------

    resume_text_lower = resume_text.lower()

    # -----------------------------------------------------
    # Explicit job-title evidence
    # -----------------------------------------------------

    role_title_boosts = {

        "IT Project Manager": [
            "it project manager",
            "project manager",
            "it project management"
        ],

        "Software Engineer": [
            "software engineer",
            "software developer"
        ],

        "Backend Developer": [
            "backend developer",
            "backend engineer"
        ],

        "Frontend Developer": [
            "frontend developer",
            "frontend engineer"
        ],

        "Data Analyst": [
            "data analyst",
            "data analysis"
        ],

        "Machine Learning Engineer": [
            "machine learning engineer",
            "ml engineer"
        ],

        "Business Analyst": [
            "business analyst"
        ],

        "Electrical Engineer": [
            "electrical engineer"
        ],

        "Electronics Engineer": [
            "electronics engineer"
        ],

        "Civil Engineer": [
            "civil engineer"
        ],

        "Mechanical Engineer": [
            "mechanical engineer"
        ],

        "Travel Consultant": [
            "travel consultant",
            "travel agent"
        ]

    }


    # -----------------------------------------------------
    # Experience evidence
    # -----------------------------------------------------

    experience_indicators = [

        "years of experience",
        "years experience",
        "work experience",
        "professional experience",
        "employment history",
        "worked as",
        "working as",
        "project manager",
        "software engineer",
        "software developer",
        "developer",
        "engineer",
        "manager"

    ]


    experience_evidence = 0

    for indicator in experience_indicators:

        pattern = (
            r'(?<!\w)'
            + re.escape(indicator)
            + r'(?!\w)'
        )

        if re.search(
            pattern,
            resume_text_lower
        ):

            experience_evidence += 1


    # -----------------------------------------------------
    # Convert experience evidence to a small boost
    # -----------------------------------------------------

    experience_boost = min(
        experience_evidence * 2,
        10
    )


    # -----------------------------------------------------
    # Create resume embedding
    # -----------------------------------------------------

    resume_embedding = model.encode(
        [resume_text],
        normalize_embeddings=True
    )


    # -----------------------------------------------------
    # Get role names
    # -----------------------------------------------------

    role_names = list(
        ROLE_PROFILES.keys()
    )


    # -----------------------------------------------------
    # Get role descriptions
    # -----------------------------------------------------

    role_descriptions = [

        ROLE_PROFILES[role]["description"]

        for role in role_names

    ]


    # -----------------------------------------------------
    # Create role embeddings
    # -----------------------------------------------------

    role_embeddings = model.encode(
        role_descriptions,
        normalize_embeddings=True
    )


    # -----------------------------------------------------
    # Calculate semantic similarity
    # -----------------------------------------------------

    similarities = cosine_similarity(
        resume_embedding,
        role_embeddings
    )[0]


    recommendations = []


    # =====================================================
    # PROCESS EACH CAREER ROLE
    # =====================================================

    for role, similarity in zip(
        role_names,
        similarities
    ):

        # -------------------------------------------------
        # Semantic score
        # -------------------------------------------------

        semantic_score_value = (
            (similarity + 1) / 2
        ) * 100

        semantic_score_value = float(
            semantic_score_value
        )


        # -------------------------------------------------
        # Explicit title boost
        # -------------------------------------------------

        title_boost = 0

        title_keywords = role_title_boosts.get(
            role,
            []
        )


        for title in title_keywords:

            pattern = (
                r'(?<!\w)'
                + re.escape(title.lower())
                + r'(?!\w)'
            )

            if re.search(
                pattern,
                resume_text_lower
            ):

                title_boost = 15

                break


        # -------------------------------------------------
        # Keyword evidence
        # -------------------------------------------------

        keywords = ROLE_PROFILES[role]["keywords"]

        matched_keywords = []


        for keyword in keywords:

            pattern = (
                r'(?<!\w)'
                + re.escape(
                    keyword.lower()
                )
                + r'(?!\w)'
            )


            if re.search(
                pattern,
                resume_text_lower
            ):

                matched_keywords.append(
                    keyword
                )


        # -------------------------------------------------
        # Keyword score
        # -------------------------------------------------

        if keywords:

            keyword_score = (
                len(matched_keywords)
                / len(keywords)
            ) * 100

        else:

            keyword_score = 0


        keyword_score = float(
            keyword_score
        )


        # -------------------------------------------------
        # Combined AI career score
        #
        # Semantic similarity  = 45%
        # Keyword evidence     = 35%
        # Explicit title       = up to 15 points
        # Experience evidence  = up to 10 points
        # -------------------------------------------------

        combined_score = (

            (semantic_score_value * 0.45)

            +

            (keyword_score * 0.35)

            +

            title_boost

            +

            experience_boost

        )


        # -------------------------------------------------
        # Keep score within 0-100
        # -------------------------------------------------

        combined_score = min(
            float(combined_score),
            100.0
        )


        # -------------------------------------------------
        # Generate explanation
        # -------------------------------------------------

        if matched_keywords:

            reason = (
                "Matched skills and experience: "
                + ", ".join(
                    matched_keywords
                )
            )

        else:

            reason = (
                "Semantic similarity with "
                "the career role."
            )


        # -------------------------------------------------
        # Add recommendation
        # -------------------------------------------------

        recommendations.append({

            "role": role,

            "match_score": round(
                combined_score,
                2
            ),

            "semantic_score": round(
                semantic_score_value,
                2
            ),

            "keyword_score": round(
                keyword_score,
                2
            ),

            "title_boost": round(
                float(title_boost),
                2
            ),

            "experience_boost": round(
                float(experience_boost),
                2
            ),

            "matched_keywords": (
                matched_keywords
            ),

            "reason": reason

        })


    # =====================================================
    # SORT BY FINAL MATCH SCORE
    # =====================================================

    recommendations.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )


    # =====================================================
    # REMOVE WEAK RECOMMENDATIONS
    # =====================================================

    recommendations = [

        recommendation

        for recommendation in recommendations

        if recommendation["match_score"] >= 45

    ]


    # =====================================================
    # RETURN TOP RECOMMENDATIONS
    # =====================================================

    return recommendations[:top_n]