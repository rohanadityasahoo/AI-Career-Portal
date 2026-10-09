import os
from flask import Flask, redirect, render_template, url_for
from routes.about import about
from routes.auth import auth
from routes.chatbot import chatbot
from routes.dashboard import dashboard
from routes.interview import interview
from routes.profile import profile
from routes.resume import resume
from routes.roadmap import roadmap

app = Flask(__name__)

# ============================================================
# FLASK CONFIGURATION
# ============================================================

app.secret_key = os.getenv("SECRET_KEY", "careerpilot-development-secret-key")

# Limit file uploads to 16 MB maximum
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


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
# ERROR HANDLERS
# ============================================================


@app.errorhandler(404)
def not_found_error(error):
  return (
      render_template(
          "home/index.html",
          info_message="The requested page could not be found.",
      ),
      404,
  )


@app.errorhandler(413)
def file_too_large_error(error):
  return (
      render_template(
          "resume/upload.html",
          error="The uploaded file is too large. Maximum allowed size is 16 MB.",
      ),
      413,
  )


@app.errorhandler(500)
def internal_server_error(error):
  return (
      render_template(
          "home/index.html",
          error="An unexpected server error occurred. Please try again later.",
      ),
      500,
  )


# ============================================================
# HOME
# ============================================================


@app.route("/")
def home():
  return render_template("home/index.html")


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
  port = int(os.getenv("PORT", "5000"))
  debug = os.getenv("FLASK_DEBUG", "0") == "1"

  app.run(host="0.0.0.0", port=port, debug=debug)