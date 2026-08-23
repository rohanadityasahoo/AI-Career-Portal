from ai_modules.semantic_analyzer import calculate_semantic_similarity


resume = """
Developed REST APIs using Python and Flask.
Built backend applications using MySQL.
Worked on web application development.
"""


job_description = """
Looking for a Python backend developer
with experience in REST API development,
Flask and database technologies.
"""


score = calculate_semantic_similarity(
    resume,
    job_description
)

print("AI Semantic Similarity:", score)