from ai_modules.skill_analyzer import match_job_description


resume = """
Developed REST APIs using Python and Flask.
Built backend applications using MySQL.
Created web applications and worked with Git.
"""


job_description = """
We are looking for a Python backend developer
with experience in REST API development,
web applications, Flask and database systems.
"""


result = match_job_description(
    resume,
    job_description
)


print("\nKeyword Match:")
print(result["keyword_match_percentage"])


print("\nAI Semantic Match:")
print(result["semantic_match_percentage"])


print("\nEnhanced JD Match:")
print(result["match_percentage"])


print("\nMatched Skills:")
print(result["matched_skills"])


print("\nMissing Skills:")
print(result["missing_skills"])