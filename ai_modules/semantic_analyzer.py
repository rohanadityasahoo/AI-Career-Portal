import gc
from ai_modules.ai_resume_analyzer import encode_texts


def calculate_semantic_similarity(resume_text, job_description):
  """Calculate semantic similarity between resume text and job description.

  Returns a score between 0 and 100.
  """
  if not resume_text or not resume_text.strip():
    return 0.0

  if not job_description or not job_description.strip():
    return 0.0

  # Generate normalized embeddings using the shared singleton model
  embeddings = encode_texts([resume_text, job_description])

  if len(embeddings) < 2:
    return 0.0

  resume_embedding = embeddings[0]
  job_embedding = embeddings[1]

  # Because embeddings are normalized, dot product equals cosine similarity
  similarity = float(resume_embedding @ job_embedding)

  # Convert cosine similarity (-1 to 1) into a 0 to 100 percentage
  score = similarity * 100

  # Clean up temporary references
  del embeddings, resume_embedding, job_embedding
  gc.collect()

  return round(float(max(0.0, min(100.0, score))), 2)