from flask import Blueprint, render_template, request
from ai_modules.roadmap_generator import generate_roadmap

roadmap = Blueprint("roadmap", __name__)

@roadmap.route("/roadmap", methods=["GET", "POST"])
def roadmap_page():

    roadmap_steps = None

    if request.method == "POST":

        career = request.form.get("career")

        roadmap_steps = generate_roadmap(
            career
        )

    return render_template(
        "roadmap/index.html",
        roadmap_steps=roadmap_steps
    )