from sentence_transformers import SentenceTransformer


MODEL_NAME = "intfloat/multilingual-e5-small"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding for a single text chunk.
    """

    text = text.strip()

    if not text:
        raise ValueError("Text cannot be empty")

    embedding = model.encode(
        f"passage: {text}",
        normalize_embeddings=True
    )

    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple text chunks.
    """

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        return []

    embeddings = model.encode(
        [f"passage: {text}" for text in cleaned_texts],
        normalize_embeddings=True
    )

    return embeddings.tolist()
