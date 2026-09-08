from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from ai_modules.interview_analyzer import (
    evaluate_answer as evaluate_answer_ai,
    get_question_pool
)
from database.db import get_db_connection


interview = Blueprint('interview', __name__)

TOTAL_QUESTIONS = 5
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


# ============================================================
# ROLE -> INTERVIEW DOMAIN MAPPING
# ============================================================

ROLE_TO_DOMAIN = {

    # ========================================================
    # INFORMATION TECHNOLOGY
    # ========================================================

    "software_engineer": "Information Technology",
    "python_developer": "Information Technology",
    "java_developer": "Information Technology",
    "cpp_developer": "Information Technology",
    "javascript_developer": "Information Technology",
    "web_developer": "Information Technology",
    "frontend_developer": "Information Technology",
    "backend_developer": "Information Technology",
    "full_stack_developer": "Information Technology",
    "django_developer": "Information Technology",
    "flask_developer": "Information Technology",
    "data_scientist": "Information Technology",
    "data_analyst": "Information Technology",
    "machine_learning_engineer": "Information Technology",
    "ai_engineer": "Information Technology",
    "devops_engineer": "Information Technology",
    "cloud_engineer": "Information Technology",
    "cybersecurity_analyst": "Information Technology",
    "database_administrator": "Information Technology",
    "software_tester": "Information Technology",
    "qa_engineer": "Information Technology",
    "system_administrator": "Information Technology",
    "it_support_specialist": "Information Technology",
    "it_project_manager": "Information Technology",
    "business_analyst": "Information Technology",


    # ========================================================
    # ELECTRICAL
    # ========================================================

    "electrical_engineer": "Electrical Engineering",
    "power_systems_engineer": "Electrical Engineering",
    "electrical_design_engineer": "Electrical Engineering",
    "control_systems_engineer": "Electrical Engineering",
    "power_electronics_engineer": "Electrical Engineering",
    "automation_engineer": "Electrical Engineering",
    "plc_engineer": "Electrical Engineering",
    "scada_engineer": "Electrical Engineering",
    "maintenance_engineer": "Electrical Engineering",


    # ========================================================
    # ELECTRONICS
    # ========================================================

    "electronics_engineer": "Electronics Engineering",
    "embedded_systems_engineer": "Electronics Engineering",
    "embedded_c_developer": "Electronics Engineering",
    "vlsi_engineer": "Electronics Engineering",
    "pcb_design_engineer": "Electronics Engineering",
    "iot_engineer": "Electronics Engineering",
    "hardware_engineer": "Electronics Engineering",
    "firmware_engineer": "Electronics Engineering",
    "robotics_engineer": "Electronics Engineering",


    # ========================================================
    # MECHANICAL
    # ========================================================

    "mechanical_engineer": "Mechanical Engineering",
    "design_engineer": "Mechanical Engineering",
    "cad_engineer": "Mechanical Engineering",
    "manufacturing_engineer": "Mechanical Engineering",
    "production_engineer": "Mechanical Engineering",
    "quality_engineer": "Mechanical Engineering",
    "automotive_engineer": "Mechanical Engineering",
    "thermal_engineer": "Mechanical Engineering",


    # ========================================================
    # CIVIL
    # ========================================================

    "civil_engineer": "Civil Engineering",
    "structural_engineer": "Civil Engineering",
    "construction_engineer": "Civil Engineering",
    "site_engineer": "Civil Engineering",
    "quantity_surveyor": "Civil Engineering",
    "planning_engineer": "Civil Engineering",
    "geotechnical_engineer": "Civil Engineering",
    "transportation_engineer": "Civil Engineering",
    "environmental_engineer": "Civil Engineering",


    # ========================================================
    # MICROBIOLOGY
    # ========================================================

    "microbiologist": "Microbiology",
    "clinical_microbiologist": "Microbiology",
    "food_microbiologist": "Microbiology",
    "industrial_microbiologist": "Microbiology",
    "research_microbiologist": "Microbiology",
    "quality_control_microbiologist": "Microbiology",


    # ========================================================
    # BIOTECHNOLOGY
    # ========================================================

    "biotechnologist": "Biotechnology",
    "research_associate": "Biotechnology",
    "bioinformatics_analyst": "Biotechnology",
    "bioprocess_engineer": "Biotechnology",
    "clinical_research_associate": "Biotechnology",
    "genetics_researcher": "Biotechnology",


    # ========================================================
    # PHARMACY
    # ========================================================

    "pharmacist": "Pharmacy",
    "clinical_pharmacist": "Pharmacy",
    "hospital_pharmacist": "Pharmacy",
    "pharmaceutical_researcher": "Pharmacy",
    "drug_safety_associate": "Pharmacy",
    "pharmacovigilance_associate": "Pharmacy",
    "quality_control_pharmacist": "Pharmacy",


    # ========================================================
    # HEALTHCARE
    # ========================================================

    "healthcare_professional": "Healthcare",
    "medical_assistant": "Healthcare",
    "medical_laboratory_technician": "Healthcare",
    "healthcare_administrator": "Healthcare",
    "medical_representative": "Healthcare",
    "public_health_professional": "Healthcare",


    # ========================================================
    # NURSING
    # ========================================================

    "staff_nurse": "Nursing",
    "registered_nurse": "Nursing",
    "clinical_nurse": "Nursing",
    "community_health_nurse": "Nursing",
    "nursing_assistant": "Nursing",
    "nurse_educator": "Nursing",


    # ========================================================
    # FINANCE & ACCOUNTING
    # ========================================================

    "accountant": "Finance & Accounting",
    "financial_analyst": "Finance & Accounting",
    "investment_analyst": "Finance & Accounting",
    "banking_associate": "Finance & Accounting",
    "credit_analyst": "Finance & Accounting",
    "tax_consultant": "Finance & Accounting",
    "audit_associate": "Finance & Accounting",
    "finance_manager": "Finance & Accounting",
    "accounts_executive": "Finance & Accounting",


    # ========================================================
    # MARKETING & SALES
    # ========================================================

    "marketing_executive": "Marketing & Sales",
    "digital_marketing_specialist": "Marketing & Sales",
    "seo_specialist": "Marketing & Sales",
    "social_media_manager": "Marketing & Sales",
    "content_marketing_specialist": "Marketing & Sales",
    "sales_executive": "Marketing & Sales",
    "business_development_executive": "Marketing & Sales",
    "sales_manager": "Marketing & Sales",
    "brand_manager": "Marketing & Sales",


    # ========================================================
    # HUMAN RESOURCES
    # ========================================================

    "hr_executive": "Human Resources",
    "hr_manager": "Human Resources",
    "recruiter": "Human Resources",
    "talent_acquisition_specialist": "Human Resources",
    "hr_business_partner": "Human Resources",
    "training_development_specialist": "Human Resources",
    "payroll_specialist": "Human Resources",


    # ========================================================
    # TRAVEL & TOURISM
    # ========================================================

    "travel_consultant": "Travel & Tourism",
    "travel_agent": "Travel & Tourism",
    "travel_coordinator": "Travel & Tourism",
    "travel_operations_executive": "Travel & Tourism",
    "tour_coordinator": "Travel & Tourism",
    "tourism_executive": "Travel & Tourism",
    "destination_planner": "Travel & Tourism",
    "tour_operator": "Travel & Tourism",
    "reservation_executive": "Travel & Tourism",
    "event_management_executive": "Travel & Tourism",


    # ========================================================
    # HOSPITALITY
    # ========================================================

    "hotel_manager": "Hospitality & Hotel Management",
    "front_office_executive": "Hospitality & Hotel Management",
    "guest_relations_executive": "Hospitality & Hotel Management",
    "food_beverage_manager": "Hospitality & Hotel Management",
    "restaurant_manager": "Hospitality & Hotel Management",
    "housekeeping_manager": "Hospitality & Hotel Management",
    "event_manager": "Hospitality & Hotel Management",
    "hospitality_executive": "Hospitality & Hotel Management",


    # ========================================================
    # EDUCATION
    # ========================================================

    "teacher": "Education",
    "lecturer": "Education",
    "professor": "Education",
    "academic_researcher": "Education",
    "school_counselor": "Education",
    "education_coordinator": "Education",


    # ========================================================
    # DESIGN & CREATIVE
    # ========================================================

    "graphic_designer": "Design & Creative",
    "ui_ux_designer": "Design & Creative",
    "product_designer": "Design & Creative",
    "content_writer": "Design & Creative",
    "technical_writer": "Design & Creative",
    "journalist": "Design & Creative",
    "video_editor": "Design & Creative",


    # ========================================================
    # ARCHITECTURE
    # ========================================================

    "architect": "Architecture",
    "interior_designer": "Architecture",
    "urban_planner": "Architecture",
    "landscape_architect": "Architecture",


    # ========================================================
    # LEGAL
    # ========================================================

    "lawyer": "Legal",
    "legal_associate": "Legal",
    "legal_advisor": "Legal",
    "corporate_lawyer": "Legal",
    "legal_researcher": "Legal",


    # ========================================================
    # MANAGEMENT & OPERATIONS
    # ========================================================

    "project_manager": "Management & Operations",
    "operations_manager": "Management & Operations",
    "operations_executive": "Management & Operations",
    "supply_chain_analyst": "Management & Operations",
    "logistics_coordinator": "Management & Operations",
    "procurement_specialist": "Management & Operations",
    "management_trainee": "Management & Operations",


    # ========================================================
    # OTHER
    # ========================================================

    "entrepreneur": "Management & Operations",
    "researcher": "Research",
    "consultant": "Management & Operations",
    "customer_service_executive": "Customer Service"
}


# ============================================================
# GET INTERVIEW DOMAIN
# ============================================================

def get_interview_domain(role):

    if not role:
        return None

    role = role.strip().lower()

    return ROLE_TO_DOMAIN.get(role)


# ============================================================
# START INTERVIEW
# ============================================================

@interview.route('/interview', methods=['GET', 'POST'])
def interview_home():

    if request.method == 'POST':

        role = (request.form.get('role') or '').strip()
        difficulty = (request.form.get('difficulty') or '').strip().lower()

        if not role or not difficulty:
            return render_template(
                'interview/index.html',
                error='Choose both a role and difficulty to begin.',
                selected_role=role,
                selected_difficulty=difficulty or 'medium'
            ), 400

        if difficulty not in VALID_DIFFICULTIES:
            return render_template(
                'interview/index.html',
                error='Choose a valid interview difficulty.',
                selected_role=role,
                selected_difficulty='medium'
            ), 400

        # Convert selected role into question-bank domain
        domain = get_interview_domain(role)

        if not domain:
            return render_template(
                'interview/index.html',
                error='That role is not supported yet. Please choose a role from the list.',
                selected_role=role,
                selected_difficulty=difficulty
            ), 400

        # Start new interview session

        session['interview_role'] = role
        session['interview_domain'] = domain
        session['interview_difficulty'] = difficulty

        session['interview_question_number'] = 1
        session['interview_scores'] = []

        # Generate a role-specific question pool using the mapped domain.

        question_pool = get_question_pool(
            role,
            difficulty,
            domain=domain
        )

        if not question_pool:

            return render_template(
                'interview/index.html',
                error='No questions are available for that selection. Please try another role or difficulty.',
                selected_role=role,
                selected_difficulty=difficulty
            ), 400

        # Remove first question from pool

        question = question_pool.pop(0)

        session['interview_questions'] = question_pool
        session['current_question'] = question

        return render_template(
            'interview/question.html',

            question=question,

            role=role,

            domain=domain,

            difficulty=difficulty,

            question_number=1,

            total_questions=TOTAL_QUESTIONS
        )

    return render_template(
        'interview/index.html',
        selected_role='',
        selected_difficulty='medium'
    )


# ============================================================
# INTERVIEW HISTORY
# ============================================================

@interview.route('/interview/history')
def interview_history():

    if 'student_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select
            interview_id,
            role,
            domain,
            difficulty,
            average_score,
            question_scores,
            created_at
        from interview_results
        where student_id=%s
        order by created_at desc
        """,
        (session['student_id'],)
    )

    interviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'interview/history.html',
        interviews=interviews
    )


# ============================================================
# EVALUATE ANSWER
# ============================================================

@interview.route('/interview/evaluate', methods=['POST'])
def evaluate_answer():

    answer = (request.form.get('answer') or '').strip()

    # The current question is stored when the interview starts. Keeping it
    # in the session makes sure the answer is scored against the question
    # that was actually displayed to the student.
    question = session.get('current_question')

    role = session.get(
        'interview_role'
    )

    domain = session.get(
        'interview_domain'
    )

    difficulty = session.get(
        'interview_difficulty'
    )

    question_number = session.get(
        'interview_question_number',
        1
    )

    scores = session.get(
        'interview_scores',
        []
    )

    if not answer:
        return render_template(
            'interview/question.html',
            question=question,
            role=role,
            domain=domain,
            difficulty=difficulty,
            question_number=question_number,
            total_questions=TOTAL_QUESTIONS,
            error='Write an answer before continuing.'
        ), 400

    if not role or not difficulty or not question:

        return redirect(
            url_for(
                'interview.interview_home'
            )
        )


    # ========================================================
    # EVALUATE ANSWER AGAINST ACTUAL QUESTION
    # ========================================================

    result = evaluate_answer_ai(
        answer,
        question,
        role=role,
        difficulty=difficulty
    )

    score = result.get(
        'score',
        0
    )

    scores.append(score)

    session['interview_scores'] = scores


    # ========================================================
    # INTERVIEW COMPLETE
    # ========================================================

    if question_number >= TOTAL_QUESTIONS:

        total_score = sum(scores)

        average_score = round(
            total_score / len(scores),
            2
        )


        if average_score >= 80:

            overall_feedback = (
                "Excellent interview performance. "
                "Your answers demonstrate strong "
                "understanding, relevance and communication."
            )

        elif average_score >= 60:

            overall_feedback = (
                "Good interview performance. "
                "You have a solid foundation, but "
                "your answers can be more detailed "
                "and supported with practical examples."
            )

        elif average_score >= 40:

            overall_feedback = (
                "Average interview performance. "
                "Focus on improving technical depth, "
                "clarity and the use of relevant examples."
            )

        else:

            overall_feedback = (
                "Your interview performance needs "
                "improvement. Practice answering "
                "questions directly and explaining "
                "concepts with examples."
            )


        # Store a compact interview summary. The student ID remains empty
        # for visitors who use the public practice feature.
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            insert into interview_results
            (
                student_id,
                role,
                domain,
                difficulty,
                average_score,
                question_scores
            )
            values (%s,%s,%s,%s,%s,%s)
            """,
            (
                session.get('student_id'),
                role,
                domain,
                difficulty,
                average_score,
                ", ".join(map(str, scores))
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        for key in (
            'interview_role',
            'interview_domain',
            'interview_difficulty',
            'interview_question_number',
            'interview_scores',
            'interview_questions',
            'current_question'
        ):
            session.pop(key, None)


        return render_template(
            'interview/final_result.html',

            role=role,

            domain=domain,

            difficulty=difficulty,

            scores=scores,

            total_questions=TOTAL_QUESTIONS,

            average_score=average_score,

            feedback=overall_feedback
        )


    # ========================================================
    # NEXT QUESTION
    # ========================================================

    question_number += 1

    session['interview_question_number'] = (
        question_number
    )


    # Use the questions created when the interview began. This keeps
    # every five-question interview consistent and prevents repeats.
    question_pool = session.get(
        'interview_questions',
        []
    )

    if not question_pool:

        return (
            "The interview question session has ended. "
            "Please start a new interview."
        )

    next_question = question_pool.pop(0)

    session['interview_questions'] = question_pool


    session['current_question'] = next_question


    return render_template(
        'interview/question.html',

        question=next_question,

        role=role,

        domain=domain,

        difficulty=difficulty,

        question_number=question_number,

        total_questions=TOTAL_QUESTIONS,

        previous_score=score,

        previous_feedback=result.get(
            'feedback',
            ''
        ),

        previous_strengths=result.get(
            'strengths',
            []
        ),

        previous_improvements=result.get(
            'improvements',
            []
        ),

        previous_rubric=result.get(
            'rubric',
            {}
        )
    )
