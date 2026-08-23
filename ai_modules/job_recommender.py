# ============================================================
# JOB RECOMMENDER
# ============================================================

def recommend_jobs(all_skills, limit=10):

    if not all_skills:
        return []

    # Convert everything to lowercase
    skills = {
        str(skill).strip().lower()
        for skill in all_skills
        if skill
    }

    # ========================================================
    # JOB DATABASE
    # ========================================================

    job_profiles = {

        # ----------------------------------------------------
        # SOFTWARE / IT
        # ----------------------------------------------------

        "Python Developer": [
            "python",
            "django",
            "flask",
            "fastapi",
            "pandas",
            "numpy"
        ],

        "Java Developer": [
            "java",
            "spring",
            "spring boot",
            "hibernate"
        ],

        "C/C++ Developer": [
            "c",
            "c++",
            "cpp"
        ],

        "JavaScript Developer": [
            "javascript",
            "typescript",
            "node.js",
            "nodejs"
        ],

        "Frontend Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "angular",
            "vue",
            "bootstrap",
            "tailwind"
        ],

        "Backend Developer": [
            "python",
            "java",
            "django",
            "flask",
            "fastapi",
            "node.js",
            "nodejs",
            "express",
            "api",
            "mysql",
            "sql"
        ],

        "Full Stack Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "node.js",
            "nodejs",
            "python",
            "django",
            "flask",
            "mysql",
            "sql"
        ],

        "Software Engineer": [
            "python",
            "java",
            "c",
            "c++",
            "javascript",
            "software development",
            "programming",
            "algorithms"
        ],

        "Web Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "angular",
            "vue",
            "node.js",
            "django",
            "flask"
        ],

        "Django Developer": [
            "python",
            "django"
        ],

        "Python Backend Developer": [
            "python",
            "django",
            "flask",
            "fastapi",
            "api"
        ],

        "Database Developer": [
            "sql",
            "mysql",
            "oracle",
            "postgresql",
            "mongodb",
            "sqlite",
            "redis"
        ],

        "Database Administrator": [
            "mysql",
            "oracle",
            "postgresql",
            "mongodb",
            "sql",
            "database"
        ],

        "Data Analyst": [
            "python",
            "sql",
            "excel",
            "pandas",
            "numpy",
            "data analysis",
            "data visualization",
            "statistics"
        ],

        "Data Scientist": [
            "python",
            "machine learning",
            "data science",
            "pandas",
            "numpy",
            "scikit-learn",
            "statistics"
        ],

        "Machine Learning Engineer": [
            "python",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "tensorflow",
            "pytorch",
            "scikit-learn"
        ],

        "AI Engineer": [
            "python",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "nlp",
            "tensorflow",
            "pytorch"
        ],

        "Cybersecurity Analyst": [
            "cybersecurity",
            "network security",
            "ethical hacking",
            "penetration testing",
            "security",
            "linux",
            "firewall"
        ],

        "Network Engineer": [
            "networking",
            "network",
            "cisco",
            "routing",
            "switching",
            "tcp/ip",
            "linux"
        ],

        "DevOps Engineer": [
            "docker",
            "kubernetes",
            "linux",
            "git",
            "github",
            "ci/cd",
            "aws",
            "azure"
        ],

        "Cloud Engineer": [
            "aws",
            "azure",
            "google cloud",
            "cloud computing",
            "docker",
            "kubernetes",
            "linux"
        ],

        "IT Support Engineer": [
            "linux",
            "windows",
            "networking",
            "troubleshooting",
            "hardware",
            "technical support"
        ],

        "IT Project Manager": [
            "project manager",
            "project management",
            "agile",
            "scrum",
            "jira",
            "sdlc",
            "project planning"
        ],

        "Business Analyst": [
            "business analysis",
            "requirements analysis",
            "business requirements",
            "stakeholders",
            "process improvement",
            "documentation"
        ],

        # ----------------------------------------------------
        # ELECTRICAL
        # ----------------------------------------------------

        "Electrical Engineer": [
            "electrical",
            "electrical engineering",
            "power systems",
            "electrical machines",
            "matlab",
            "simulink",
            "control systems",
            "circuit analysis"
        ],

        "Power Systems Engineer": [
            "power systems",
            "electrical machines",
            "electrical engineering",
            "matlab",
            "etap",
            "pscad"
        ],

        "Electrical Design Engineer": [
            "electrical design",
            "circuit analysis",
            "electrical engineering",
            "autocad",
            "matlab"
        ],

        "Control Systems Engineer": [
            "control systems",
            "matlab",
            "simulink",
            "plc",
            "scada"
        ],

        "PLC/SCADA Engineer": [
            "plc",
            "scada",
            "control systems",
            "industrial automation"
        ],

        # ----------------------------------------------------
        # ELECTRONICS
        # ----------------------------------------------------

        "Electronics Engineer": [
            "electronics",
            "electronics engineering",
            "embedded systems",
            "microcontroller",
            "microprocessor",
            "pcb design"
        ],

        "Embedded Systems Engineer": [
            "embedded systems",
            "embedded c",
            "microcontroller",
            "microprocessor",
            "arduino",
            "raspberry pi"
        ],

        "IoT Engineer": [
            "iot",
            "internet of things",
            "arduino",
            "raspberry pi",
            "embedded systems",
            "microcontroller"
        ],

        "VLSI Engineer": [
            "vlsi",
            "verilog",
            "vhdl",
            "fpga",
            "digital design"
        ],

        "PCB Design Engineer": [
            "pcb design",
            "electronics",
            "circuit design"
        ],

        # ----------------------------------------------------
        # CIVIL
        # ----------------------------------------------------

        "Civil Engineer": [
            "civil engineering",
            "civil",
            "autocad",
            "structural analysis",
            "construction"
        ],

        "Structural Engineer": [
            "structural analysis",
            "structural design",
            "civil engineering",
            "staad pro",
            "staad.pro"
        ],

        "Site Engineer": [
            "site engineering",
            "construction",
            "civil engineering",
            "construction management",
            "surveying"
        ],

        "Construction Engineer": [
            "construction",
            "construction management",
            "civil engineering",
            "project management"
        ],

        "Quantity Surveyor": [
            "quantity surveying",
            "quantity surveyor",
            "cost estimation",
            "construction"
        ],

        "Planning Engineer": [
            "planning engineer",
            "construction planning",
            "project planning",
            "construction management"
        ],

        "AutoCAD Civil Designer": [
            "autocad",
            "civil 3d",
            "civil engineering",
            "structural design"
        ],

        # ----------------------------------------------------
        # MECHANICAL
        # ----------------------------------------------------

        "Mechanical Engineer": [
            "mechanical engineering",
            "mechanical design",
            "thermodynamics",
            "fluid mechanics",
            "manufacturing"
        ],

        "Mechanical Design Engineer": [
            "mechanical design",
            "solidworks",
            "catia",
            "creo",
            "cad",
            "3d modeling"
        ],

        "CAD Engineer": [
            "cad",
            "autocad",
            "solidworks",
            "catia",
            "creo",
            "3d modeling"
        ],

        "Manufacturing Engineer": [
            "manufacturing",
            "mechanical engineering",
            "cam",
            "production",
            "manufacturing processes"
        ],

        "Automotive Engineer": [
            "automotive",
            "automotive engineering",
            "vehicle design",
            "mechanical design",
            "manufacturing"
        ],

        "Aerospace Engineer": [
            "aerospace",
            "aerodynamics",
            "aircraft",
            "propulsion",
            "mechanical engineering"
        ],

        # ----------------------------------------------------
        # FINANCE / ACCOUNTING
        # ----------------------------------------------------

        "Accountant": [
            "accounting",
            "financial accounting",
            "bookkeeping",
            "tally",
            "tally erp",
            "accounts payable",
            "accounts receivable"
        ],

        "Financial Analyst": [
            "finance",
            "financial analysis",
            "financial modeling",
            "investment analysis",
            "budgeting",
            "forecasting"
        ],

        "Audit Associate": [
            "auditing",
            "audit",
            "accounting",
            "financial accounting"
        ],

        "Tax Consultant": [
            "taxation",
            "tax",
            "gst",
            "income tax",
            "accounting"
        ],

        "Banking Associate": [
            "banking",
            "finance",
            "financial analysis",
            "customer service"
        ],

        "Investment Analyst": [
            "investment analysis",
            "finance",
            "financial modeling",
            "financial analysis"
        ],

        # ----------------------------------------------------
        # MARKETING / SALES
        # ----------------------------------------------------

        "Marketing Executive": [
            "marketing",
            "digital marketing",
            "marketing strategy",
            "brand management"
        ],

        "Digital Marketing Specialist": [
            "digital marketing",
            "seo",
            "sem",
            "google ads",
            "social media marketing",
            "email marketing"
        ],

        "SEO Specialist": [
            "seo",
            "search engine optimization",
            "content marketing"
        ],

        "Sales Executive": [
            "sales",
            "sales management",
            "customer service",
            "lead generation"
        ],

        "Business Development Executive": [
            "business development",
            "sales",
            "lead generation",
            "customer acquisition"
        ],

        "Social Media Manager": [
            "social media marketing",
            "social media",
            "content marketing",
            "digital marketing"
        ],

        # ----------------------------------------------------
        # HUMAN RESOURCES
        # ----------------------------------------------------

        "HR Executive": [
            "human resources",
            "hr",
            "hr operations",
            "employee relations"
        ],

        "Recruitment Specialist": [
            "recruitment",
            "talent acquisition",
            "human resources",
            "hiring"
        ],

        "Talent Acquisition Specialist": [
            "talent acquisition",
            "recruitment",
            "human resources"
        ],

        "HR Analyst": [
            "hr analytics",
            "human resources",
            "data analysis",
            "workforce planning"
        ],

        # ----------------------------------------------------
        # TRAVEL / TOURISM
        # ----------------------------------------------------

        "Travel Consultant": [
            "travel",
            "tourism",
            "travel consultant",
            "travel consulting",
            "travel planning",
            "itineraries",
            "reservations",
            "hospitality"
        ],

        "Travel Agent": [
            "travel agent",
            "travel",
            "tourism",
            "reservations",
            "ticketing",
            "travel planning"
        ],

        "Tour Coordinator": [
            "tourism",
            "tour planning",
            "tour coordinator",
            "itineraries",
            "travel coordination",
            "travel"
        ],

        "Travel Coordinator": [
            "travel coordination",
            "travel planning",
            "reservations",
            "itineraries",
            "tourism"
        ],

        "Tourism Executive": [
            "tourism",
            "travel",
            "hospitality",
            "tour packages",
            "destination management"
        ],

        "Reservation Executive": [
            "reservations",
            "hotel reservations",
            "airline reservations",
            "ticketing",
            "hospitality"
        ],

        "Tour Operator": [
            "tour operator",
            "tourism",
            "tour packages",
            "itineraries",
            "travel planning"
        ],

        "Destination Planner": [
            "destination management",
            "travel planning",
            "tourism",
            "itineraries",
            "event planning"
        ],

        "Travel Operations Executive": [
            "travel operations",
            "travel coordination",
            "reservations",
            "tourism",
            "customer service"
        ],

        # ----------------------------------------------------
        # HOSPITALITY
        # ----------------------------------------------------

        "Hotel Management Executive": [
            "hotel management",
            "hospitality",
            "hotel operations",
            "guest relations",
            "reservations"
        ],

        "Front Office Executive": [
            "front office",
            "hotel management",
            "guest relations",
            "hospitality",
            "reservations"
        ],

        "Guest Relations Executive": [
            "guest relations",
            "hospitality",
            "customer service",
            "hotel operations"
        ],

        "Food & Beverage Executive": [
            "food and beverage",
            "restaurant management",
            "hospitality",
            "catering",
            "banquet management"
        ],

        "Event Management Executive": [
            "event management",
            "event planning",
            "hospitality",
            "customer service"
        ],

        # ----------------------------------------------------
        # HEALTHCARE
        # ----------------------------------------------------

        "Healthcare Administrator": [
            "healthcare",
            "health administration",
            "hospital management",
            "medical records",
            "patient care"
        ],

        "Health Informatics Analyst": [
            "health informatics",
            "healthcare",
            "clinical data",
            "data analysis",
            "medical records"
        ],

        "Medical Records Executive": [
            "medical records",
            "healthcare",
            "medical terminology",
            "patient care"
        ],

        "Clinical Research Assistant": [
            "clinical research",
            "healthcare",
            "clinical data",
            "research"
        ],

        "Public Health Analyst": [
            "public health",
            "epidemiology",
            "healthcare",
            "statistics"
        ],

        # ----------------------------------------------------
        # NURSING
        # ----------------------------------------------------

        "Registered Nurse": [
            "nursing",
            "registered nurse",
            "patient care",
            "clinical nursing"
        ],

        "Staff Nurse": [
            "nursing",
            "staff nurse",
            "patient care",
            "clinical assessment"
        ],

        "ICU Nurse": [
            "nursing",
            "critical care",
            "icu",
            "patient care"
        ],

        "Community Health Nurse": [
            "nursing",
            "community health nursing",
            "public health",
            "patient care"
        ],

        "Emergency Nurse": [
            "nursing",
            "emergency nursing",
            "first aid",
            "patient care"
        ],

        # ----------------------------------------------------
        # PHARMACY
        # ----------------------------------------------------

        "Pharmacist": [
            "pharmacy",
            "pharmacology",
            "dispensing",
            "clinical pharmacy"
        ],

        "Clinical Pharmacist": [
            "clinical pharmacy",
            "pharmacy",
            "pharmacology",
            "patient care"
        ],

        "Pharmaceutical Quality Analyst": [
            "pharmacy",
            "quality control",
            "quality assurance",
            "pharmaceutical chemistry"
        ],

        "Pharmacovigilance Associate": [
            "pharmacovigilance",
            "drug safety",
            "pharmacy",
            "pharmacology"
        ],

        # ----------------------------------------------------
        # MICROBIOLOGY
        # ----------------------------------------------------

        "Microbiologist": [
            "microbiology",
            "microbiologist",
            "bacteriology",
            "microbial culture"
        ],

        "Clinical Microbiologist": [
            "clinical microbiology",
            "microbiology",
            "pathology",
            "bacteriology"
        ],

        "Food Microbiologist": [
            "food microbiology",
            "microbiology",
            "food technology",
            "quality control"
        ],

        "Laboratory Technician": [
            "microbiology",
            "laboratory",
            "microscopy",
            "microbial culture",
            "pcr"
        ],

        "Quality Control Analyst": [
            "quality control",
            "microbiology",
            "laboratory",
            "quality assurance"
        ],

        # ----------------------------------------------------
        # BIOTECHNOLOGY
        # ----------------------------------------------------

        "Biotechnologist": [
            "biotechnology",
            "biotech",
            "molecular biology",
            "cell culture"
        ],

        "Biotechnology Research Assistant": [
            "biotechnology",
            "research",
            "molecular biology",
            "genetic engineering"
        ],

        "Bioinformatics Analyst": [
            "bioinformatics",
            "biotechnology",
            "genomics",
            "data analysis",
            "python"
        ],

        "Molecular Biology Researcher": [
            "molecular biology",
            "genomics",
            "pcr",
            "genetic engineering"
        ],

        # ----------------------------------------------------
        # CHEMISTRY
        # ----------------------------------------------------

        "Chemist": [
            "chemistry",
            "analytical chemistry",
            "organic chemistry",
            "inorganic chemistry"
        ],

        "Laboratory Analyst": [
            "chemistry",
            "laboratory",
            "analytical chemistry",
            "quality control"
        ],

        "Chemical Quality Analyst": [
            "chemistry",
            "quality control",
            "quality assurance",
            "laboratory"
        ],

        # ----------------------------------------------------
        # AGRICULTURE
        # ----------------------------------------------------

        "Agricultural Officer": [
            "agriculture",
            "agricultural science",
            "crop production",
            "soil science"
        ],

        "Agronomist": [
            "agronomy",
            "agriculture",
            "crop management",
            "soil science"
        ],

        "Agricultural Research Assistant": [
            "agriculture",
            "research",
            "plant science",
            "crop production"
        ],

        # ----------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------

        "Environmental Scientist": [
            "environmental science",
            "environmental management",
            "environmental impact assessment"
        ],

        "Environmental Engineer": [
            "environmental engineering",
            "waste management",
            "water treatment",
            "environmental science"
        ],

        # ----------------------------------------------------
        # ARCHITECTURE
        # ----------------------------------------------------

        "Architect": [
            "architecture",
            "architectural design",
            "autocad",
            "revit",
            "3d modeling"
        ],

        "Architectural Designer": [
            "architectural design",
            "autocad",
            "revit",
            "3d modeling"
        ],

        "Interior Designer": [
            "interior design",
            "autocad",
            "3d modeling",
            "design"
        ],

        # ----------------------------------------------------
        # UI / UX / DESIGN
        # ----------------------------------------------------

        "UI Designer": [
            "ui design",
            "user interface",
            "figma",
            "adobe xd",
            "design"
        ],

        "UX Designer": [
            "ux design",
            "user experience",
            "figma",
            "user research"
        ],

        "Graphic Designer": [
            "graphic design",
            "photoshop",
            "illustrator",
            "adobe",
            "canva"
        ],

        # ----------------------------------------------------
        # MEDIA
        # ----------------------------------------------------

        "Content Writer": [
            "content writing",
            "copywriting",
            "content marketing",
            "writing"
        ],

        "Journalist": [
            "journalism",
            "reporting",
            "news writing",
            "media"
        ],

        "Social Media Content Creator": [
            "social media",
            "content creation",
            "content marketing",
            "digital marketing"
        ],

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        "Teacher": [
            "teaching",
            "education",
            "lesson planning",
            "classroom management"
        ],

        "School Teacher": [
            "teaching",
            "education",
            "lesson planning",
            "classroom management"
        ],

        "Lecturer": [
            "teaching",
            "education",
            "lecturing",
            "academic"
        ],

        "Academic Research Assistant": [
            "research",
            "academic",
            "education",
            "data analysis"
        ],

        # ----------------------------------------------------
        # LEGAL
        # ----------------------------------------------------

        "Legal Associate": [
            "law",
            "legal",
            "legal research",
            "contract",
            "litigation"
        ],

        "Legal Research Assistant": [
            "legal research",
            "law",
            "legal",
            "research"
        ],

        "Compliance Analyst": [
            "compliance",
            "legal",
            "risk management",
            "regulatory"
        ],

        # ----------------------------------------------------
        # LOGISTICS
        # ----------------------------------------------------

        "Logistics Coordinator": [
            "logistics",
            "supply chain",
            "inventory management",
            "transportation"
        ],

        "Supply Chain Analyst": [
            "supply chain",
            "logistics",
            "inventory management",
            "procurement",
            "data analysis"
        ],

        "Procurement Executive": [
            "procurement",
            "purchasing",
            "supply chain",
            "vendor management"
        ],

        # ----------------------------------------------------
        # AVIATION
        # ----------------------------------------------------

        "Aviation Operations Executive": [
            "aviation",
            "airport operations",
            "airline operations",
            "travel",
            "customer service"
        ],

        "Airline Reservation Executive": [
            "airline reservations",
            "reservations",
            "ticketing",
            "travel",
            "aviation"
        ],

        # ----------------------------------------------------
        # SPORTS
        # ----------------------------------------------------

        "Fitness Trainer": [
            "fitness",
            "personal training",
            "strength training",
            "exercise"
        ],

        "Sports Coach": [
            "sports",
            "coaching",
            "athletics",
            "training"
        ]
    }

    # ========================================================
    # CALCULATE MATCHES
    # ========================================================

    scored_jobs = []

    for job_title, required_skills in job_profiles.items():

        matched = []

        for required_skill in required_skills:

            required_skill = required_skill.lower()

            # Exact match
            if required_skill in skills:
                matched.append(required_skill)
                continue

            # Partial match
            for user_skill in skills:

                if (
                    required_skill in user_skill
                    or user_skill in required_skill
                ):
                    matched.append(required_skill)
                    break

        matched = list(dict.fromkeys(matched))

        if not matched:
            continue

        match_percentage = (
            len(matched) / len(required_skills)
        ) * 100

        scored_jobs.append(
            (
                job_title,
                match_percentage,
                len(matched)
            )
        )

    # ========================================================
    # SORT
    # ========================================================

    scored_jobs.sort(
        key=lambda x: (x[1], x[2]),
        reverse=True
    )

    # ========================================================
    # RETURN ONLY JOB TITLES
    #
    # This keeps compatibility with your existing
    # resume/result.html template.
    # ========================================================

    return [
        job[0]
        for job in scored_jobs[:limit]
    ]