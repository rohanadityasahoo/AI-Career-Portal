from ai_modules.skill_analyzer import detect_skills


resume_text = """
Bachelor of Technology in Computer Science Engineering

Technical Skills:
Python, Java, C++, JavaScript, HTML, CSS
Flask, Django, MySQL, SQL
Git, GitHub, Docker
Machine Learning, Pandas, NumPy

Projects:
Developed a Flask web application using Python and MySQL.
Implemented machine learning models using Python and scikit-learn.
"""


result = detect_skills(resume_text)

print("\nDetected Skills:\n")

for category, skills in result.items():

    print(category, ":", skills)