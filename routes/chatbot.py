from database.db import get_db_connection
from flask import Blueprint, redirect, render_template, request, session, url_for
from ai_modules.career_ai import generate_chat_guidance
from ai_modules.usage import ai_feature_context

chatbot = Blueprint('chatbot', __name__)

# Flask's default session is a signed browser cookie. Keep enough context for a
# natural follow-up while keeping the stored transcript deliberately compact.
CHAT_HISTORY_LIMIT = 2
MAX_MESSAGE_LENGTH = 800
MAX_STORED_RESPONSE_LENGTH = 820


def _student_context():
    """Load only the profile fields that can make coaching more relevant."""
    student_id = session.get('student_id')
    if not student_id:
        return None

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.profile_type, s.branch, s.year,
                       COALESCE(fresher_profile.career_goal, professional_profile.career_switch_reason) AS career_goal,
                       COALESCE(fresher_profile.target_role, professional_profile.target_role) AS target_role,
                       COALESCE(fresher_profile.preferred_industry, professional_profile.current_industry, professional_profile.target_field) AS preferred_industry,
                       COALESCE(fresher_profile.preferred_location, professional_profile.preferred_location) AS preferred_location,
                       professional_profile.current_job_title,
                       professional_profile.current_company,
                       professional_profile.key_skills,
                       professional_profile.job_search_status,
                       professional_profile.target_companies,
                       professional_profile.employment_type,
                       professional_profile.work_preference,
                       professional_profile.relocation_preference,
                       professional_profile.career_highlights
                FROM students AS s
                LEFT JOIN student_profile AS fresher_profile
                    ON fresher_profile.student_id = s.student_id
                   AND s.profile_type = 'fresher'
                LEFT JOIN professional_profile
                    ON professional_profile.student_id = s.student_id
                   AND s.profile_type = 'experienced'
                WHERE s.student_id = %s
                """,
                (student_id,),
            )
            return cursor.fetchone()
    except Exception:
        # Coaching can still work for an anonymous user or if the profile
        # lookup is temporarily unavailable.
        return None
    finally:
        if conn:
            conn.close()


def _normalise_history(value):
    """Read both old plain-text turns and the compact current session shape."""
    if not isinstance(value, list):
        return []

    history = []
    for turn in value[-CHAT_HISTORY_LIMIT:]:
        if not isinstance(turn, dict):
            continue
        question = str(turn.get('question', '')).strip()[:MAX_MESSAGE_LENGTH]
        answer = str(turn.get('answer') or turn.get('response') or '').strip()
        if question and answer:
            history.append({
                'question': question,
                'answer': answer[:MAX_STORED_RESPONSE_LENGTH],
                'ai_assisted': bool(turn.get('ai_assisted')),
            })
    return history


def _compact_turn(question, guidance):
    """Persist only the useful conversational context, never a full AI payload."""
    return {
        'question': question[:MAX_MESSAGE_LENGTH],
        'answer': str(guidance.get('answer', ''))[:MAX_STORED_RESPONSE_LENGTH],
        'ai_assisted': bool(guidance.get('ai_assisted')),
    }


@chatbot.route('/chatbot', methods=['GET', 'POST'])
def chatbot_home():

    error = ""
    user_message = ""
    latest_guidance = None
    chat_history = _normalise_history(session.get('chat_history', []))

    if request.method == 'POST':

        user_message = request.form.get('question', '').strip()

        if not user_message:
            error = "Please enter a career-related question."

        elif len(user_message) > MAX_MESSAGE_LENGTH:
            error = (
                "Please keep your question within "
                f"{MAX_MESSAGE_LENGTH} characters."
            )

        else:
            with ai_feature_context('career_chatbot', session.get('student_id')):
                latest_guidance = generate_chat_guidance(
                    user_message,
                    student_context=_student_context(),
                    chat_history=chat_history,
                )
            if not latest_guidance:
                error = (
                    'Career guidance could not be prepared. Please try again '
                    'in a moment.'
                )
            else:
                session['chat_history'] = (
                    chat_history + [_compact_turn(user_message, latest_guidance)]
                )[-CHAT_HISTORY_LIMIT:]

    return render_template(
        'chatbot/index.html',
        error=error,
        chat_history=chat_history,
        latest_guidance=latest_guidance,
        user_message=user_message,
    )


@chatbot.route('/chatbot/clear', methods=['POST'])
def clear_chat():

    session.pop('chat_history', None)

    return redirect(
        url_for('chatbot.chatbot_home')
    )
