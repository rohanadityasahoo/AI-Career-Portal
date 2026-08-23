import pdfplumber


def extract_resume_text(pdf_path):

    extracted_text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

    print("\n========== EXTRACTED RESUME TEXT ==========")
    print(extracted_text[:5000])
    print("========== END RESUME TEXT ==========\n")

    return extracted_text