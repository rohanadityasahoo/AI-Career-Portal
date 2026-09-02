from flask import Blueprint, request, session, jsonify, redirect, render_template
from ai_modules.roadmap_generator import generate_roadmap
from database.db import get_db_connection, ensure_career_roadmaps_table
import json

roadmap = Blueprint("roadmap", __name__)


@roadmap.route("/roadmap", methods=["GET", "POST"])
def roadmap_page():
    if "student_id" not in session:
        if request.method == "POST" and request.is_json:
            return jsonify({"error": "Student not logged in"}), 401
        return redirect("/login")

    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT target_role
            FROM student_profile
            WHERE student_id = %s
            """,
            (session["student_id"],)
        )
        career_profile = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template(
            "roadmap/index.html",
            roadmap_steps=None,
            target_role=(career_profile or {}).get("target_role", "")
        )

    data = request.get_json(silent=True) if request.is_json else request.form

    target_role = (data.get("target_role") or data.get("career") or "").strip()

    if not target_role:
        if not request.is_json:
            return render_template(
                "roadmap/index.html",
                roadmap_steps=None,
                error="Target role is required."
            ), 400
        return jsonify({"error": "Target role is required"}), 400

    roadmap_data = generate_roadmap(target_role)

    if roadmap_data == ["Roadmap not available"]:
        message = (
            f"A roadmap for '{target_role}' is not available yet. "
            "Try Python Developer, Data Scientist, or Software Engineer."
        )
        if request.is_json:
            return jsonify({"error": message}), 400
        return render_template(
            "roadmap/index.html",
            roadmap_steps=None,
            target_role=target_role,
            unsupported_message=message
        ), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    ensure_career_roadmaps_table(cursor)

    cursor.execute("""
        INSERT INTO career_roadmaps
        (student_id, target_role, roadmap_json)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        target_role = VALUES(target_role),
        roadmap_json = VALUES(roadmap_json)
    """, (
        session["student_id"],
        target_role,
        json.dumps(roadmap_data)
    ))

    conn.commit()
    cursor.close()
    conn.close()

    if request.is_json:
        return jsonify({
            "target_role": target_role,
            "roadmap": roadmap_data
        })

    return render_template(
        "roadmap/index.html",
        target_role=target_role,
        roadmap_steps=roadmap_data
    )
