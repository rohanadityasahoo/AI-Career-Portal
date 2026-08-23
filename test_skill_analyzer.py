from ai_modules.skill_analyzer import (
    detect_skills,
    match_job_description,
    detect_sections,
    calculate_skill_score,
    calculate_section_score,
    calculate_content_score,
    calculate_ats_score
)


sample_resume = """
Rohan Aditya Sahoo

Education

B.Tech Computer Science student.

Technical Skills

Python, Java, C++, SQL, MySQL, Flask,
Pandas, NumPy, Scikit-Learn, Git and GitHub.

Projects

Developed a machine learning project using Python.
Created a Flask web application with MySQL.
Implemented an AI based career portal.

Certifications

Python Programming Certification.

Achievements

Completed multiple software development projects.
"""


job_description = """
We are looking for a software developer with
Python, Flask, MySQL, SQL, Git, JavaScript,
React, Docker and Machine Learning skills.
"""


# Skill detection
detected_skills = detect_skills(sample_resume)

skill_score = calculate_skill_score(
    detected_skills
)


# Job description matching
jd_result = match_job_description(
    sample_resume,
    job_description
)


jd_match_percentage = jd_result["match_percentage"]


# Resume sections
detected_sections = detect_sections(
    sample_resume
)

section_score = calculate_section_score(
    detected_sections
)


# Content quality
content_score = calculate_content_score(
    sample_resume
)


# Final ATS score
ats_score = calculate_ats_score(
    jd_match_percentage,
    skill_score,
    section_score,
    content_score
)


print("\n========== RESUME ANALYSIS ==========")

print("\nDetected Skills:")
print(detected_skills)

print("\nJob Match:")
print(jd_match_percentage, "%")

print("\nMissing Skills:")
print(jd_result["missing_skills"])

print("\nResume Sections:")
print(detected_sections)

print("\nSection Score:")
print(section_score)

print("\nSkill Score:")
print(skill_score)

print("\nContent Score:")
print(content_score)

print("\nFINAL ATS SCORE:")
print(ats_score, "/ 100")