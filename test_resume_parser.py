from ai_modules.resume_parser import extract_text_from_pdf


resume_path = "sample_resume.pdf"

text = extract_text_from_pdf(
    resume_path
)

print(text)