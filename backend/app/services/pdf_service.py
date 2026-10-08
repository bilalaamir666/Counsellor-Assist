import pymupdf


def extract_pdf_pages(file_path: str):
    pages = []

    document = pymupdf.open(file_path)

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "content": text
                })

    finally:
        document.close()

    return pages
