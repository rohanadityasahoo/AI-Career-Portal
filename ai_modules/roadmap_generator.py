import re

# ============================================================
# CURATED ROADMAP KNOWLEDGE BASE
# ============================================================

ROADMAPS = {
    # --------------------------------------------------------
    # SOFTWARE & WEB DEVELOPMENT
    # --------------------------------------------------------
    "python developer": [
        "Master Python fundamentals (data structures, OOP, file handling)",
        "Learn web frameworks (Flask or Django) and RESTful API design",
        "Master relational databases (MySQL, PostgreSQL) & ORMs (SQLAlchemy)",
        "Implement authentication, security best practices, and caching",
        "Learn Git, GitHub, virtual environments, and package management",
        (
            "Build 2-3 full-stack portfolio projects with end-to-end"
            " functionality"
        ),
        "Deploy applications on cloud platforms (Docker, Render, AWS)",
        "Prepare for technical interviews and apply for junior roles",
    ],
    "software engineer": [
        (
            "Learn a primary programming language thoroughly (Python, Java, or"
            " C++)"
        ),
        (
            "Master Data Structures and Algorithms (Arrays, Trees, Graphs, DP)"
            " on LeetCode"
        ),
        "Learn database management, SQL, and database normalization",
        (
            "Understand Software Engineering principles (Design Patterns, OOP,"
            " System Design basics)"
        ),
        "Learn version control (Git) and collaborative workflows",
        (
            "Build robust software applications demonstrating clean code"
            " practices"
        ),
        "Practice coding tests, mock interviews, and system architecture",
        "Apply for internships, campus drives, and entry-level positions",
    ],
    "java developer": [
        "Master Core Java (OOP, Collections Framework, Multithreading, Streams)",
        "Learn Build Tools (Maven/Gradle) and JUnit for unit testing",
        "Master relational databases and SQL queries",
        (
            "Learn Spring Framework & Spring Boot for microservices and REST"
            " APIs"
        ),
        "Learn Spring Data JPA / Hibernate for ORM",
        (
            "Build enterprise-grade applications with secure JWT/OAuth"
            " authentication"
        ),
        "Containerize services using Docker and explore CI/CD pipelines",
        "Practice Java design patterns and interview problem solving",
    ],
    "frontend developer": [
        "Master semantic HTML5, modern CSS3, Flexbox, and CSS Grid",
        "Master modern JavaScript (ES6+, DOM manipulation, Fetch API, Async/Await)",
        "Learn CSS frameworks and preprocessors (Tailwind CSS or Bootstrap)",
        (
            "Master a major modern frontend library/framework (React, Vue, or"
            " Angular)"
        ),
        "Learn State Management (Redux Toolkit, Context API, or Zustand)",
        (
            "Understand web performance, responsive design, and SEO"
            " fundamentals"
        ),
        "Build interactive web applications consuming RESTful APIs",
        "Deploy projects on Vercel/Netlify and showcase an active GitHub portfolio",
    ],
    "backend developer": [
        (
            "Master a server-side language (Python, Node.js/TypeScript, Java, or"
            " Go)"
        ),
        "Learn web servers and RESTful / GraphQL API architectures",
        "Master SQL (PostgreSQL, MySQL) and NoSQL databases (MongoDB, Redis)",
        "Implement secure user authentication (JWT, OAuth2, session management)",
        "Learn microservices, message queues (RabbitMQ, Kafka), and Docker",
        "Write integration tests and optimize database query performance",
        "Deploy and monitor APIs using AWS/GCP and automated CI/CD",
        "Study System Design fundamentals (caching, load balancing, sharding)",
    ],
    "full stack developer": [
        "Master frontend essentials (HTML, CSS, JavaScript, React.js)",
        "Master a backend stack (Node.js/Express, Python/Flask/Django, or Java/Spring)",
        "Design relational and document databases with optimized schemas",
        "Build full-featured applications connecting frontend to backend APIs",
        "Implement state management, authentication, and payment gateways",
        "Learn Docker, container orchestration, and cloud deployment",
        "Practice system architecture and end-to-end testing",
        "Publish live projects with source code documentation",
    ],
    # --------------------------------------------------------
    # DATA SCIENCE & ARTIFICIAL INTELLIGENCE
    # --------------------------------------------------------
    "data scientist": [
        "Master Python for data science (NumPy, Pandas, Matplotlib, Seaborn)",
        "Study Mathematics for ML (Linear Algebra, Calculus, Probability & Statistics)",
        "Master advanced SQL and data wrangling techniques",
        "Learn Classical Machine Learning (Scikit-Learn: Regression, Trees, Clustering)",
        (
            "Learn Deep Learning fundamentals using PyTorch or TensorFlow /"
            " Keras"
        ),
        (
            "Work on end-to-end data science projects (EDA, feature"
            " engineering, modeling)"
        ),
        "Learn model deployment (Streamlit, FastAPI) and MLOps basics",
        (
            "Publish Jupyter Notebooks and Kaggle case studies to your"
            " portfolio"
        ),
    ],
    "data analyst": [
        "Master Advanced Microsoft Excel (Pivot tables, VLOOKUP/XLOOKUP, formulas)",
        (
            "Master SQL for querying, joins, aggregations, and window functions"
            " (MySQL/PostgreSQL)"
        ),
        "Learn Business Intelligence & visualization tools (Power BI or Tableau)",
        "Learn Python for exploratory data analysis (Pandas, Matplotlib, Seaborn)",
        "Understand business metrics, KPI tracking, and statistical hypothesis testing",
        "Build interactive dashboards and actionable business case studies",
        "Develop data storytelling and presentation skills",
        "Apply for internships and data analyst roles",
    ],
    "machine learning engineer": [
        "Master Python, object-oriented programming, and scientific computing",
        "Deep dive into algorithms (gradient descent, loss functions, regularization)",
        "Master Scikit-Learn, PyTorch, and Deep Learning architectures (CNNs, RNNs, Transformers)",
        "Learn Natural Language Processing (NLP) or Computer Vision techniques",
        "Learn Data Engineering pipelines (ETL, feature stores, data validation)",
        "Learn MLOps: Model versioning (MLflow, DVC), Docker, and model serving APIs",
        "Deploy production ML models on cloud platforms (AWS SageMaker, GCP Vertex AI)",
        "Contribute to open-source ML repositories and showcase case studies",
    ],
    # --------------------------------------------------------
    # CLOUD, DEVOPS & SECURITY
    # --------------------------------------------------------
    "devops engineer": [
        "Master Linux administration, shell scripting (Bash), and networking basics",
        "Master Git branching strategies and GitOps workflows",
        "Learn containerization with Docker and container security",
        "Master container orchestration with Kubernetes",
        "Implement Infrastructure as Code (IaC) using Terraform or Ansible",
        "Build automated CI/CD pipelines (GitHub Actions, GitLab CI, or Jenkins)",
        "Learn Cloud Platforms (AWS, Azure, or Google Cloud Platform)",
        "Configure logging, monitoring, and alerting (Prometheus, Grafana)",
    ],
    "cybersecurity analyst": [
        "Master networking fundamentals (TCP/IP, OSI model, DNS, subnets)",
        "Learn Linux & Windows operating system security and administration",
        "Understand security concepts (threat modeling, encryption, firewalls, SIEM)",
        "Learn vulnerability scanning and penetration testing tools (Wireshark, Nmap, Burp Suite)",
        "Study ethical hacking techniques and security governance frameworks",
        "Participate in CTF (Capture The Flag) competitions and TryHackMe challenges",
        "Prepare for industry certifications (CompTIA Security+, CEH)",
        "Apply for SOC (Security Operations Center) analyst and security roles",
    ],
    # --------------------------------------------------------
    # CORE ENGINEERING (ELECTRICAL, ELECTRONICS, MECHANICAL, CIVIL)
    # --------------------------------------------------------
    "electrical engineer": [
        "Master circuit analysis, network theorems, and electrical machines",
        "Learn power systems, transmission, distribution, and protection relays",
        "Learn simulation and modeling software (MATLAB, Simulink, ETAP, PSCAD)",
        "Master industrial automation fundamentals (PLC programming, SCADA systems)",
        "Understand electrical switchgear, safety codes, and standards (IEEE, IEC)",
        "Work on practical electrical design or renewable energy projects",
        "Gain hands-on industrial plant or substation internship experience",
        "Prepare for competitive exams and core industrial engineering roles",
    ],
    "electronics engineer": [
        "Master analog and digital electronics, circuit design, and semiconductors",
        "Learn microcontroller architectures (ARM Cortex, AVR, PIC, ESP32)",
        "Master Embedded C / C++ programming and communication protocols (UART, SPI, I2C)",
        "Learn PCB design and schematic capture using KiCad or Altium Designer",
        "Learn digital system design with Verilog / VHDL on FPGA boards",
        "Build practical hardware prototypes and IoT sensor systems",
        "Test and debug circuits using oscilloscopes, logic analyzers, and multimeters",
        "Apply for embedded hardware, firmware, and IoT engineering positions",
    ],
    "mechanical engineer": [
        "Master engineering mechanics, strength of materials, and machine design",
        "Learn thermodynamics, fluid mechanics, and manufacturing processes",
        "Master 3D CAD modeling software (SolidWorks, CATIA, or Autodesk Inventor)",
        "Learn FEA and CFD simulation tools (ANSYS, Abaqus)",
        "Understand GD&T (Geometric Dimensioning and Tolerancing) and blueprint reading",
        "Work on robotics, automotive, or product design projects",
        "Gain hands-on workshop, machining, and industrial manufacturing experience",
        "Apply for design engineer, production, or automotive engineering roles",
    ],
    "civil engineer": [
        "Master structural analysis, fluid mechanics, and surveying",
        "Learn building materials, concrete technology, and geotechnical engineering",
        "Master design and drafting tools (AutoCAD, Revit, STAAD.Pro, ETABS)",
        "Understand building codes, structural estimation, and cost surveying",
        "Study construction project management, safety protocols, and quality control",
        "Work on residential/commercial structural design projects",
        "Gain on-site construction supervision and site inspection internship experience",
        "Apply for structural, site engineering, and urban planning positions",
    ],
    # --------------------------------------------------------
    # MANAGEMENT, LIFE SCIENCES & BUSINESS
    # --------------------------------------------------------
    "it project manager": [
        "Master Software Development Life Cycle (SDLC) models (Agile, Scrum, Waterfall)",
        "Learn project management tools (Jira, Confluence, Trello, Asana)",
        "Develop scope, timeline, and budget management skills",
        "Master stakeholder communication, risk management, and conflict resolution",
        "Study Agile ceremonies, sprint planning, and backlog grooming",
        "Earn recognized certifications (Scrum Master - CSM, CAPM, or PMP)",
        "Lead technical projects or cross-functional team initiatives",
        "Apply for associate project manager or technical project coordinator roles",
    ],
    "business analyst": [
        "Learn requirements elicitation, process modeling, and flowcharts (UML, BPMN)",
        "Master data analysis with Excel and SQL for business insights",
        "Learn BI dashboarding with Power BI or Tableau",
        "Understand Business Requirements Documents (BRD) and User Stories",
        "Practice stakeholder interviewing and gap analysis",
        "Build case studies analyzing business problems and proposed solutions",
        "Learn Agile project environments and Jira",
        "Apply for junior business analyst and management trainee positions",
    ],
    "microbiologist": [
        "Master bacteriology, virology, mycology, and microbial genetics",
        "Develop aseptic lab techniques, microbial culturing, and staining methods",
        "Learn molecular biology techniques (PCR, gel electrophoresis, ELISA)",
        "Study quality control (QC) and Good Laboratory Practices (GLP)",
        "Understand pharmaceutical microbiology, food testing, and water analysis",
        "Conduct academic research or laboratory projects",
        "Gain hands-on experience in diagnostic labs or industrial QA/QC",
        "Apply for research assistant or quality control microbiologist positions",
    ],
}


# ============================================================
# ROLE NORMALIZATION & SYNONYM MAPPING
# ============================================================

ROLE_SYNONYMS = {
    "python": "python developer",
    "python dev": "python developer",
    "django developer": "python developer",
    "flask developer": "python developer",
    "software dev": "software engineer",
    "software developer": "software engineer",
    "sde": "software engineer",
    "programmer": "software engineer",
    "coder": "software engineer",
    "web developer": "frontend developer",
    "web dev": "frontend developer",
    "react developer": "frontend developer",
    "front end developer": "frontend developer",
    "back end developer": "backend developer",
    "fullstack developer": "full stack developer",
    "fullstack": "full stack developer",
    "ml engineer": "machine learning engineer",
    "ai engineer": "machine learning engineer",
    "artificial intelligence": "machine learning engineer",
    "deep learning engineer": "machine learning engineer",
    "cloud engineer": "devops engineer",
    "site reliability engineer": "devops engineer",
    "sre": "devops engineer",
    "security analyst": "cybersecurity analyst",
    "electrical": "electrical engineer",
    "electronics": "electronics engineer",
    "embedded engineer": "electronics engineer",
    "iot engineer": "electronics engineer",
    "mechanical": "mechanical engineer",
    "cad engineer": "mechanical engineer",
    "civil": "civil engineer",
    "structural engineer": "civil engineer",
    "project manager": "it project manager",
    "scrum master": "it project manager",
    "biotechnologist": "microbiologist",
    "biotechnology": "microbiologist",
}


def _clean_role(role_name):
  """Cleans and standardizes the input role string."""
  if not role_name:
    return ""
  cleaned = str(role_name).lower().strip()
  # Replace underscores, hyphens, and multi-spaces with single space
  cleaned = re.sub(r"[_\-]+", " ", cleaned)
  cleaned = re.sub(r"\s+", " ", cleaned)
  return cleaned


def _generate_generic_roadmap(role_title):
  """Builds a comprehensive 7-step roadmap for any role not in the knowledge base."""
  title = role_title.title()
  return [
      f"Master fundamental concepts, theoretical principles, and core tools"
      f" for {title}",
      (
          "Learn industry-standard software, primary development environments,"
          " and workflows"
      ),
      (
          "Build 2-3 practical, portfolio-worthy projects demonstrating"
          " real-world problem solving"
      ),
      (
          "Study intermediate and advanced domain topics, design patterns, and"
          " architectures"
      ),
      (
          "Learn version control, documentation, and quality assurance best"
          " practices"
      ),
      (
          f"Prepare a tailored, ATS-friendly resume and practice mock {title}"
          " interview questions"
      ),
      (
          "Engage in professional networking, open-source/internship"
          f" opportunities, and apply for {title} roles"
      ),
  ]


# ============================================================
# MAIN GENERATOR FUNCTION
# ============================================================


def generate_roadmap(career):
  """Generates a step-by-step career roadmap for the requested career/role.

  Always returns a structured list of actionable steps.
  """
  cleaned = _clean_role(career)

  if not cleaned:
    return ["Please specify a target role to generate your career roadmap."]

  # 1. Exact match in knowledge base
  if cleaned in ROADMAPS:
    return ROADMAPS[cleaned]

  # 2. Match via synonym / alias table
  if cleaned in ROLE_SYNONYMS:
    canonical = ROLE_SYNONYMS[cleaned]
    return ROADMAPS[canonical]

  # 3. Substring / partial match search
  for key in ROADMAPS:
    if key in cleaned or cleaned in key:
      return ROADMAPS[key]

  for synonym, canonical in ROLE_SYNONYMS.items():
    if synonym in cleaned:
      return ROADMAPS[canonical]

  # 4. Fallback: Intelligent dynamic roadmap generation
  return _generate_generic_roadmap(career)