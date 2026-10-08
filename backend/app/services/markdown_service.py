from pathlib import Path


def extract_markdown_pages(file_path: str):
    content = Path(file_path).read_text(
        encoding="utf-8"
    ).strip()

    if not content:
        return []

    return [
        {
            "page_number": 1,
            "content": content
        }
    ]
