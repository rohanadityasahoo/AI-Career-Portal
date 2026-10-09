import pdfplumber


def extract_resume_text(pdf_path):
  """Safely extracts all text from a PDF resume without leaking text to server logs."""
  extracted_text = []

  try:
    with pdfplumber.open(pdf_path) as pdf:
      for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
          extracted_text.append(page_text)
  except Exception as e:
    # Handle corrupted, encrypted, or malformed PDFs gracefully
    return ''

  return '\n'.join(extracted_text).strip()