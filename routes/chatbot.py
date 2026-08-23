from flask import Blueprint, redirect, render_template, request, session, url_for
from ai_modules.career_chatbot import get_response

chatbot = Blueprint('chatbot', __name__)

CHAT_HISTORY_LIMIT = 6
MAX_MESSAGE_LENGTH = 500


@chatbot.route('/chatbot', methods=['GET', 'POST'])
def chatbot_home():

    bot_response = ""
    error = ""
    user_message = ""
    chat_history = session.get('chat_history', [])

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
            bot_response = get_response(user_message)

            chat_history.append(
                {
                    'question': user_message,
                    'response': bot_response
                }
            )

            # Keep the browser session small while retaining recent context.
            chat_history = chat_history[-CHAT_HISTORY_LIMIT:]
            session['chat_history'] = chat_history

    return render_template(
        'chatbot/index.html',
        response=bot_response,
        error=error,
        chat_history=chat_history
    )


@chatbot.route('/chatbot/clear', methods=['POST'])
def clear_chat():

    session.pop('chat_history', None)

    return redirect(
        url_for('chatbot.chatbot_home')
    )
