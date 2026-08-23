from flask import Blueprint, render_template, request
from ai_modules.placement_predictor import predict_placement

placement = Blueprint(
    "placement",
    __name__
)

@placement.route(
    "/placement",
    methods=["GET", "POST"]
)
def placement_home():

    prediction = None
    score = None

    if request.method == "POST":

        ats = float(
            request.form["ats"]
        )

        skills = float(
            request.form["skills"]
        )

        interview = float(
            request.form["interview"]
        )

        prediction, score = predict_placement(
            ats,
            skills,
            interview
        )

    return render_template(
        "placement/index.html",
        prediction=prediction,
        score=score
    )