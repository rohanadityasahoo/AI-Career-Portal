import os

from flask import Flask, render_template

from routes.auth import auth
from routes.resume import resume
from routes.interview import interview
from routes.profile import profile
from routes.dashboard import dashboard
from routes.roadmap import roadmap
from routes.chatbot import chatbot
from routes.about import about


app = Flask(__name__)


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app.secret_key = os.getenv(
    "SECRET_KEY",
    "careerpilot-development-secret-key"
)


# ============================================================
# BLUEPRINTS
# ============================================================

app.register_blueprint(auth)
app.register_blueprint(resume)
app.register_blueprint(interview)
app.register_blueprint(profile)
app.register_blueprint(dashboard)
app.register_blueprint(roadmap)
app.register_blueprint(chatbot)
app.register_blueprint(about)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "home/index.html"
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    debug = os.getenv(
        "FLASK_DEBUG",
        "0"
    ) == "1"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )