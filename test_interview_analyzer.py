from ai_modules.interview_analyzer import generate_question


question = generate_question(
    "python_developer",
    "medium"
)

print("Interview Question:")
print(question)