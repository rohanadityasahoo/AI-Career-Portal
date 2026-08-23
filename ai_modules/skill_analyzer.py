import re
from ai_modules.semantic_analyzer import calculate_semantic_similarity

def clean_text(text):
    return text.lower()


SKILLS = {

    "programming": [
        "python",
        "java",
        "c++",
        "c",
        "c#",
        "javascript",
        "typescript",
        "go",
        "rust",
        "php"
    ],

    "web_development": [
        "html",
        "css",
        "javascript",
        "react",
        "angular",
        "vue",
        "node.js",
        "nodejs",
        "express",
        "flask",
        "django",
        "fastapi",
        "bootstrap",
        "tailwind"
    ],

    "database": [
        "mysql",
        "sql",
        "oracle",
        "postgresql",
        "mongodb",
        "sqlite",
        "redis"
    ],

    "data_science": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "data analysis",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "opencv",
        "nlp"
    ],

    "tools": [
        "git",
        "github",
        "docker",
        "kubernetes",
        "linux",
        "ubuntu",
        "vs code",
        "visual studio",
        "postman"
    ],
    
    "professional": [
        "project management",
        "project manager",
        "agile",
        "scrum",
        "jira",
        "sdlc",
        "software development lifecycle",
        "rest api",
        "restful api",
        "api",
        "stakeholder management",
        "requirements management",
        "budget management",
        "resource management",
        "risk management",
        "product management",
        "business analysis",
        "technical project management"
    ],
    
    "travel_tourism": [
        "travel",
        "tourism",
        "travel planning",
        "travel consultant",
        "travel agent",
        "travel consulting",
        "tour planning",
        "tour packages",
        "itineraries",
        "reservations",
        "ticketing",
        "airline reservations",
        "hotel reservations",
        "destination management",
        "hospitality",
        "customer service",
        "visa processing",
        "tour operator",
        "travel coordination",
        "event planning",
        "foreign exchange",
        "domestic travel",
        "international travel",
        "travel management",
        "travel coordination"
    ],

    "hospitality": [
        "hospitality",
        "hotel management",
        "hotel operations",
        "front office",
        "housekeeping",
        "food and beverage",
        "restaurant management",
        "guest relations",
        "reservations",
        "event management",
        "catering",
        "banquet management",
        "customer service",
        "tourism",
        "travel"
    ],
    
    "finance_accounting": [
        "accounting",
        "finance",
        "financial analysis",
        "financial accounting",
        "management accounting",
        "cost accounting",
        "taxation",
        "auditing",
        "audit",
        "bookkeeping",
        "accounts payable",
        "accounts receivable",
        "gst",
        "income tax",
        "tally",
        "tally erp",
        "quickbooks",
        "financial modeling",
        "investment analysis",
        "budgeting",
        "forecasting",
        "banking",
        "risk analysis",
        "corporate finance"
    ],

    "marketing_sales": [
        "marketing",
        "digital marketing",
        "social media marketing",
        "content marketing",
        "seo",
        "sem",
        "google ads",
        "facebook ads",
        "email marketing",
        "brand management",
        "market research",
        "sales",
        "business development",
        "lead generation",
        "customer acquisition",
        "crm",
        "salesforce",
        "hubspot",
        "copywriting",
        "advertising",
        "public relations"
    ],

    "human_resources": [
        "human resources",
        "hr",
        "recruitment",
        "talent acquisition",
        "talent management",
        "employee relations",
        "performance management",
        "payroll",
        "hr operations",
        "training and development",
        "learning and development",
        "onboarding",
        "hr analytics",
        "workforce planning"
    ],

    "healthcare": [
        "healthcare",
        "health care",
        "clinical research",
        "patient care",
        "medical terminology",
        "hospital management",
        "health administration",
        "medical coding",
        "medical billing",
        "public health",
        "epidemiology",
        "health informatics",
        "clinical data",
        "medical records"
    ],

    "nursing": [
        "nursing",
        "registered nurse",
        "staff nurse",
        "patient care",
        "clinical nursing",
        "community health nursing",
        "critical care",
        "icu",
        "emergency nursing",
        "midwifery",
        "pediatric nursing",
        "mental health nursing",
        "first aid",
        "clinical assessment"
    ],

    "pharmacy": [
        "pharmacy",
        "pharmacology",
        "pharmaceutics",
        "pharmaceutical chemistry",
        "pharmacognosy",
        "clinical pharmacy",
        "drug development",
        "drug formulation",
        "quality control",
        "quality assurance",
        "pharmacovigilance",
        "drug safety",
        "dispensing"
    ],

    "microbiology": [
        "microbiology",
        "microbiologist",
        "bacteriology",
        "virology",
        "mycology",
        "parasitology",
        "microbial culture",
        "gram staining",
        "microscopy",
        "sterilization",
        "pathology",
        "clinical microbiology",
        "food microbiology",
        "environmental microbiology",
        "immunology",
        "molecular biology",
        "pcr"
    ],

    "biotechnology": [
        "biotechnology",
        "biotech",
        "molecular biology",
        "genetic engineering",
        "genomics",
        "proteomics",
        "cell culture",
        "tissue culture",
        "bioinformatics",
        "recombinant dna",
        "pcr",
        "gel electrophoresis",
        "bioprocessing",
        "fermentation",
        "crispr"
    ],

    "electrical": [
        "matlab",
        "simulink",
        "plc",
        "scada",
        "power systems",
        "electrical machines",
        "power electronics",
        "control systems",
        "circuit analysis",
        "electrical design",
        "pscad",
        "etap"
    ],

    "electronics": [
        "embedded systems",
        "arduino",
        "raspberry pi",
        "microcontroller",
        "microprocessor",
        "verilog",
        "vhdl",
        "fpga",
        "pcb design",
        "embedded c",
        "iot",
        "internet of things"
    ],

    "civil": [
        "autocad",
        "staad pro",
        "staad.pro",
        "revit",
        "civil 3d",
        "structural analysis",
        "structural design",
        "surveying",
        "quantity surveying",
        "construction management",
        "concrete technology",
        "geotechnical engineering"
    ],

    "mechanical": [
        "solidworks",
        "catia",
        "ansys",
        "autocad",
        "creo",
        "3d modeling",
        "cad",
        "cam",
        "thermodynamics",
        "fluid mechanics",
        "manufacturing",
        "mechanical design"
    ]
}


def clean_text(text):

    text = text.lower()

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def detect_skills(text):

    text = clean_text(text)
    
    normalized_text = text.lower()

    normalized_text = normalized_text.replace(
        "projectmanagement",
        "project management"
    )

    normalized_text = normalized_text.replace(
        "softwaredevelopment",
        "software development"
    )

    normalized_text = normalized_text.replace(
        "businessanalysis",
        "business analysis"
    )

    normalized_text = normalized_text.replace(
        "restfulapi",
        "restful api"
    )

    normalized_text = normalized_text.replace(
        "projectmanager",
        "project manager"
    )

    detected_skills = {}

    for category, skills in SKILLS.items():

        detected_skills[category] = []

        for skill in skills:

            pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

            if re.search(pattern, text):

                detected_skills[category].append(skill)

    return detected_skills

def match_job_description(resume_text, job_description):

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    matched_skills = []
    missing_skills = []

    all_skills = []

    for skills in SKILLS.values():
        all_skills.extend(skills)

    # ==========================================
    # Traditional Keyword Matching
    # ==========================================

    for skill in all_skills:

        if skill in job_description:

            if skill in resume_text:
                matched_skills.append(skill)

            else:
                missing_skills.append(skill)

    total_required = len(matched_skills) + len(missing_skills)

    if total_required == 0:

        keyword_match_percentage = 0

    else:

        keyword_match_percentage = (
            len(matched_skills) / total_required
        ) * 100

    keyword_match_percentage = round(
        keyword_match_percentage,
        2
    )

    # ==========================================
    # AI Semantic Matching
    # ==========================================

    semantic_match_percentage = calculate_semantic_similarity(
        resume_text,
        job_description
    )

    # ==========================================
    # Combined AI + Keyword Match
    # ==========================================

    match_percentage = (
        (keyword_match_percentage * 0.40)
        +
        (semantic_match_percentage * 0.60)
    )

    match_percentage = round(
        match_percentage,
        2
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,

        # Traditional score
        "keyword_match_percentage":
            keyword_match_percentage,

        # AI score
        "semantic_match_percentage":
            semantic_match_percentage,

        # Final enhanced score
        "match_percentage":
            match_percentage
    }
    
def calculate_section_score(detected_sections):

    important_sections = [
        "education",
        "experience",
        "skills",
        "projects",
        "certifications",
        "achievements"
    ]

    found_sections = sum(
        1
        for section in important_sections
        if detected_sections.get(section, False)
    )

    score = (
        found_sections / len(important_sections)
    ) * 100

    return round(score, 2)

def calculate_content_score(resume_text):

    text = clean_text(resume_text)

    score = 0

    # Resume length
    word_count = len(text.split())

    if word_count >= 200:
        score += 40
    elif word_count >= 100:
        score += 25
    elif word_count >= 50:
        score += 15

    # Action-oriented words
    action_words = [
        "developed",
        "implemented",
        "created",
        "designed",
        "managed",
        "analyzed",
        "built",
        "improved"
    ]

    action_word_count = sum(
        1
        for word in action_words
        if word in text
    )

    if action_word_count >= 5:
        score += 30
    elif action_word_count >= 3:
        score += 20
    elif action_word_count >= 1:
        score += 10

    # Numbers / measurable results
    if any(char.isdigit() for char in text):
        score += 30

    return min(score, 100)

def calculate_resume_ats_score(
    skill_score,
    section_score,
    content_score
):
    ats_score = (
        (skill_score * 0.40)
        + (section_score * 0.30)
        + (content_score * 0.30)
    )

    return round(ats_score, 2)

def detect_sections(text):

    text = clean_text(text)

    sections = {
        "education": [
            "education",
            "academic background"
        ],

        "experience": [
            "experience",
            "work experience",
            "employment"
        ],

        "skills": [
            "skills",
            "technical skills",
            "core skills"
        ],

        "projects": [
            "projects",
            "academic projects",
            "personal projects"
        ],

        "certifications": [
            "certifications",
            "certificates"
        ],

        "achievements": [
            "achievements",
            "accomplishments"
        ]
    }

    detected_sections = {}

    for section, keywords in sections.items():

        detected_sections[section] = any(
            keyword in text
            for keyword in keywords
        )

    return detected_sections


def generate_recommendations(
    missing_skills,
    detected_sections,
    content_score
):

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Consider adding these job-relevant skills "
            "if you genuinely have them: "
            + ", ".join(missing_skills)
        )

    if not detected_sections.get("experience"):
        recommendations.append(
            "Consider adding relevant internship, "
            "training, or work experience."
        )

    if not detected_sections.get("projects"):
        recommendations.append(
            "Add relevant academic or personal projects."
        )

    if not detected_sections.get("certifications"):
        recommendations.append(
            "Add relevant certifications if available."
        )

    if content_score < 50:
        recommendations.append(
            "Improve your resume with measurable achievements "
            "and stronger action-oriented descriptions."
        )

    return recommendations


def calculate_skill_score(detected_skills):

    total_skills = sum(
        len(skills)
        for skills in detected_skills.values()
    )

    maximum_skills = sum(
        len(skills)
        for skills in SKILLS.values()
    )

    if maximum_skills == 0:
        return 0

    score = (total_skills / maximum_skills) * 100

    return round(score, 2)

def calculate_resume_ats_score(
    ai_quality_score,
    skill_score,
    section_score,
    content_score
):

    ats_score = (
        (ai_quality_score * 0.40)
        + (skill_score * 0.20)
        + (section_score * 0.20)
        + (content_score * 0.20)
    )

    return round(
        ats_score,
        2
    )
    
def detect_career_domain(detected_skills):

    domain_categories = {
        "Information Technology": ["programming", "web_development", "database", "tools", "professional"],
        "Data Science & AI": ["data_science", "programming", "database", "tools"],
        "Cybersecurity": ["cybersecurity", "networking", "programming", "tools"],
        "Networking & Telecommunications": ["networking", "telecommunications", "electronics"],
        "Electrical Engineering": ["electrical", "electronics"],
        "Electronics Engineering": ["electronics", "telecommunications", "programming"],
        "Civil Engineering": ["civil", "architecture", "environmental"],
        "Mechanical Engineering": ["mechanical", "automotive", "aerospace"],
        "Automotive Engineering": ["automotive", "mechanical", "electronics"],
        "Aerospace Engineering": ["aerospace", "mechanical", "electronics"],
        "Mining & Petroleum": ["mining_petroleum", "mechanical", "environmental"],
        "Business & Management": ["business_management", "professional"],
        "Finance & Accounting": ["finance_accounting", "business_management"],
        "Marketing & Sales": ["marketing_sales", "business_management", "professional"],
        "Human Resources": ["human_resources", "business_management", "professional"],
        "Travel & Tourism": ["travel_tourism", "hospitality", "professional"],
        "Hospitality & Hotel Management": ["hospitality", "travel_tourism", "professional"],
        "Logistics & Supply Chain": ["logistics_supply_chain", "business_management", "professional"],
        "Healthcare": ["healthcare", "professional"],
        "Nursing": ["nursing", "healthcare"],
        "Pharmacy": ["pharmacy", "healthcare"],
        "Microbiology": ["microbiology", "life_sciences", "healthcare"],
        "Biotechnology": ["biotechnology", "life_sciences", "chemistry"],
        "Life Sciences": ["life_sciences", "microbiology", "chemistry"],
        "Chemistry": ["chemistry", "life_sciences"],
        "Physics": ["physics", "electronics", "electrical"],
        "Agriculture": ["agriculture", "environmental"],
        "Environmental Science & Engineering": ["environmental", "civil", "agriculture"],
        "Food Technology": ["food_technology", "microbiology", "chemistry"],
        "Architecture": ["architecture", "design_creative", "civil"],
        "Design & Creative": ["design_creative", "media_journalism"],
        "Fashion & Textile": ["fashion_textile", "design_creative", "marketing_sales"],
        "Media & Journalism": ["media_journalism", "marketing_sales", "design_creative"],
        "Law & Legal": ["legal", "business_management", "professional"],
        "Education & Teaching": ["education_teaching", "professional"],
        "Psychology": ["psychology", "healthcare", "professional"],
        "Social Sciences & Public Policy": ["social_science", "professional"],
        "Sports & Fitness": ["sports_fitness", "healthcare", "professional"],
        "Aviation": ["aviation", "travel_tourism", "electronics"],
        "Real Estate": ["real_estate", "business_management", "professional"],
        "Operations & Quality": ["operations_quality", "business_management", "professional"]
    }

    domain_scores = {}
    for domain, categories in domain_categories.items():
        score = 0.0
        for category in categories:
            count = len(detected_skills.get(category, []))
            if count:
                score += count * (1.2 if category in {"professional", "finance_accounting", "healthcare", "nursing", "pharmacy", "microbiology", "biotechnology", "civil", "mechanical", "electrical", "electronics", "travel_tourism", "hospitality", "legal"} else 1.0)
        domain_scores[domain] = score

    best_domain = max(domain_scores, key=domain_scores.get)
    if domain_scores[best_domain] <= 0:
        return "General / Undetermined"
    return best_domain

def calculate_domain_skill_score(detected_skills, career_domain):

    domain_categories = {
        "Information Technology": ["programming", "web_development", "database", "tools", "professional"],
        "Data Science & AI": ["data_science", "programming", "database", "tools"],
        "Cybersecurity": ["cybersecurity", "networking", "programming", "tools"],
        "Networking & Telecommunications": ["networking", "telecommunications", "electronics"],
        "Electrical Engineering": ["electrical", "electronics"],
        "Electronics Engineering": ["electronics", "telecommunications", "programming"],
        "Civil Engineering": ["civil", "architecture", "environmental"],
        "Mechanical Engineering": ["mechanical", "automotive", "aerospace"],
        "Automotive Engineering": ["automotive", "mechanical", "electronics"],
        "Aerospace Engineering": ["aerospace", "mechanical", "electronics"],
        "Mining & Petroleum": ["mining_petroleum", "mechanical", "environmental"],
        "Business & Management": ["business_management", "professional"],
        "Finance & Accounting": ["finance_accounting", "business_management"],
        "Marketing & Sales": ["marketing_sales", "business_management", "professional"],
        "Human Resources": ["human_resources", "business_management", "professional"],
        "Travel & Tourism": ["travel_tourism", "hospitality", "professional"],
        "Hospitality & Hotel Management": ["hospitality", "travel_tourism", "professional"],
        "Logistics & Supply Chain": ["logistics_supply_chain", "business_management", "professional"],
        "Healthcare": ["healthcare", "professional"],
        "Nursing": ["nursing", "healthcare"],
        "Pharmacy": ["pharmacy", "healthcare"],
        "Microbiology": ["microbiology", "life_sciences", "healthcare"],
        "Biotechnology": ["biotechnology", "life_sciences", "chemistry"],
        "Life Sciences": ["life_sciences", "microbiology", "chemistry"],
        "Chemistry": ["chemistry", "life_sciences"],
        "Physics": ["physics", "electronics", "electrical"],
        "Agriculture": ["agriculture", "environmental"],
        "Environmental Science & Engineering": ["environmental", "civil", "agriculture"],
        "Food Technology": ["food_technology", "microbiology", "chemistry"],
        "Architecture": ["architecture", "design_creative", "civil"],
        "Design & Creative": ["design_creative", "media_journalism"],
        "Fashion & Textile": ["fashion_textile", "design_creative", "marketing_sales"],
        "Media & Journalism": ["media_journalism", "marketing_sales", "design_creative"],
        "Law & Legal": ["legal", "business_management", "professional"],
        "Education & Teaching": ["education_teaching", "professional"],
        "Psychology": ["psychology", "healthcare", "professional"],
        "Social Sciences & Public Policy": ["social_science", "professional"],
        "Sports & Fitness": ["sports_fitness", "healthcare", "professional"],
        "Aviation": ["aviation", "travel_tourism", "electronics"],
        "Real Estate": ["real_estate", "business_management", "professional"],
        "Operations & Quality": ["operations_quality", "business_management", "professional"]
    }

    categories = domain_categories.get(career_domain, list(SKILLS.keys()))
    caps = {category: 5 for category in SKILLS}
    caps.update({"professional": 6, "finance_accounting": 6, "travel_tourism": 6, "hospitality": 6, "healthcare": 5, "nursing": 6, "pharmacy": 6, "microbiology": 6, "biotechnology": 6, "civil": 6, "mechanical": 6, "electrical": 6, "electronics": 6})

    total = 0.0
    weight_total = 0.0
    for category in categories:
        weight = 1.2 if category in {"professional", "finance_accounting", "healthcare", "nursing", "pharmacy", "microbiology", "biotechnology", "civil", "mechanical", "electrical", "electronics", "travel_tourism", "hospitality", "legal"} else 1.0
        count = len(detected_skills.get(category, []))
        coverage = min(count / caps.get(category, 5), 1.0)
        total += coverage * weight
        weight_total += weight

    if weight_total == 0:
        return 0.0
    return round(min((total / weight_total) * 100, 100), 2)
