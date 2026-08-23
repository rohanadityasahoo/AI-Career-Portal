from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the pretrained NLP model once
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def calculate_semantic_similarity(
    resume_text,
    job_description
):
    """
    Calculate semantic similarity between
    resume text and job description.

    Returns a score between 0 and 100.
    """

    if not resume_text.strip():
        return 0.0

    if not job_description.strip():
        return 0.0

    # Convert both texts into AI embeddings
    resume_embedding = model.encode(
        [resume_text],
        convert_to_numpy=True
    )

    job_embedding = model.encode(
        [job_description],
        convert_to_numpy=True
    )

    # Calculate cosine similarity
    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    # Convert 0-1 similarity to 0-100
    score = similarity * 100

    # Keep score within 0-100
    score = max(0, min(score, 100))

    return round(float(score), 2)