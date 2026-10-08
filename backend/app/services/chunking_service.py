def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 100
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    chunks = []

    for page in pages:
        content = page["content"]
        page_number = page["page_number"]

        start = 0

        while start < len(content):
            end = start + chunk_size

            chunk_content = content[start:end].strip()

            if chunk_content:
                chunks.append({
                    "content": chunk_content,
                    "page_number": page_number,
                    "chunk_index": len(chunks)
                })

            if end >= len(content):
                break

            start = end - overlap

    return chunks
