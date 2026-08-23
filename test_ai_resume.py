from ai_modules.ai_resume_analyzer import calculate_ai_resume_quality


resume = """
IT Project Manager with experience managing software development
projects using Agile and Scrum methodologies.

Worked with engineering, product, marketing and sales teams.
Managed large software projects, budgets and schedules.

Technical skills include Python, JavaScript, Node.js, Django,
Jira and project management.

Bachelor of Science in Information Technology.

Successfully delivered projects on time and under budget.
"""


score = calculate_ai_resume_quality(resume)

print("AI Resume Quality:", score)