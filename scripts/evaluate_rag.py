import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.retrieval_service import search_similar_chunks
from app.database import db


QUESTIONS_FILE = PROJECT_ROOT / "eval" / "questions.json"
TOP_K = 5


def get_document_id_by_name(filename):
    document = db["documents"].find_one(
        {"original_filename": filename}
    )

    if document:
        return str(document["_id"])

    return None


def get_document_name(document_id):
    from bson import ObjectId

    try:
        document = db["documents"].find_one(
            {"_id": ObjectId(document_id)}
        )
    except Exception:
        return document_id

    if document:
        return document.get(
            "original_filename",
            document.get("filename", document_id)
        )

    return document_id


def evaluate_question(question_data):
    question_id = question_data["id"]
    question = question_data["question"]
    answerable = question_data["answerable"]

    print("\n" + "=" * 80)
    print(f"Question {question_id}: {question}")
    print("=" * 80, flush=True)

    # Unanswerable questions only test retrieval behaviour.
    if not answerable:
        print("Type: UNANSWERABLE", flush=True)

        try:
            results = search_similar_chunks(question, limit=TOP_K)
        except Exception as e:
            print(f"Retrieval ERROR: {e}", flush=True)
            return {
                "id": question_id,
                "passed": False,
                "reason": "Retrieval error"
            }

        print(f"Retrieved {len(results)} chunks", flush=True)

        for rank, result in enumerate(results, 1):
            print(
                f"{rank}. {get_document_name(result['document_id'])} "
                f"| Page {result['page_number']} "
                f"| Score {result.get('score', 0):.4f}",
                flush=True
            )

        print(
            "NOTE: Retrieval alone cannot prove that a question "
            "is unanswerable.",
            flush=True
        )

        return {
            "id": question_id,
            "passed": True,
            "reason": "Retrieved for later refusal evaluation"
        }

    print("Type: ANSWERABLE", flush=True)

    expected_document = question_data["expected_document"]
    expected_page = question_data["expected_page"]

    expected_document_id = get_document_id_by_name(expected_document)

    # Special handling for the renamed fees PDF.
    if expected_document_id is None:
        if "Tuition, Fees and Refund Policy" in expected_document:
            expected_document_id = get_document_id_by_name(
                "CBIU_Fees_2027.pdf"
            )

    if expected_document_id is None:
        print(
            f"ERROR: Could not find expected document: "
            f"{expected_document}",
            flush=True
        )

        return {
            "id": question_id,
            "passed": False,
            "reason": "Expected document not found in database"
        }

    print(
        f"Expected: {expected_document} | "
        f"Page {expected_page}",
        flush=True
    )

    try:
        results = search_similar_chunks(question, limit=TOP_K)
    except Exception as e:
        print(f"Retrieval ERROR: {e}", flush=True)

        return {
            "id": question_id,
            "passed": False,
            "reason": "Retrieval error"
        }

    print("\nRetrieved chunks:", flush=True)

    found_rank = None

    for rank, result in enumerate(results, 1):
        document_name = get_document_name(result["document_id"])

        print(
            f"{rank}. {document_name} "
            f"| Page {result['page_number']} "
            f"| Score {result.get('score', 0):.4f}",
            flush=True
        )

        if (
            result["document_id"] == expected_document_id
            and result["page_number"] == expected_page
            and found_rank is None
        ):
            found_rank = rank

    if found_rank is not None:
        print(
            f"\nPASS - Expected page found at rank {found_rank}",
            flush=True
        )

        return {
            "id": question_id,
            "passed": True,
            "rank": found_rank,
            "reason": f"Expected page found at rank {found_rank}"
        }

    print(
        "\nFAIL - Expected document/page not found in top-5",
        flush=True
    )

    return {
        "id": question_id,
        "passed": False,
        "reason": "Expected document/page not found in top-5"
    }


def main():
    print("=" * 80)
    print("COUNSELLOR ASSIST - RAG RETRIEVAL EVALUATION")
    print("=" * 80, flush=True)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    print(
        f"Loaded {len(questions)} questions",
        flush=True
    )

    print(
        f"Top-k retrieval: {TOP_K}",
        flush=True
    )

    results = []

    for question in questions:
        result = evaluate_question(question)
        results.append(result)

    answerable_questions = [
        q for q in questions if q["answerable"]
    ]

    answerable_results = [
        r for q, r in zip(questions, results)
        if q["answerable"]
    ]

    unanswerable_results = [
        r for q, r in zip(questions, results)
        if not q["answerable"]
    ]

    top1 = 0
    top3 = 0
    top5 = 0

    for result in answerable_results:
        if result.get("rank") is not None:
            rank = result["rank"]

            if rank <= 1:
                top1 += 1

            if rank <= 3:
                top3 += 1

            if rank <= 5:
                top5 += 1

    total_answerable = len(answerable_questions)

    print("\n" + "=" * 80)
    print("FINAL RETRIEVAL RESULTS")
    print("=" * 80)

    print(
        f"\nAnswerable questions: {total_answerable}"
    )

    print(
        f"Top-1 accuracy: "
        f"{top1}/{total_answerable} "
        f"({(top1 / total_answerable) * 100:.2f}%)"
    )

    print(
        f"Top-3 accuracy: "
        f"{top3}/{total_answerable} "
        f"({(top3 / total_answerable) * 100:.2f}%)"
    )

    print(
        f"Top-5 accuracy: "
        f"{top5}/{total_answerable} "
        f"({(top5 / total_answerable) * 100:.2f}%)"
    )

    print(
        f"\nUnanswerable questions tested: "
        f"{len(unanswerable_results)}"
    )

    print(
        "\nIMPORTANT:"
        "\nUnanswerable questions require the LLM refusal test."
        "\nThis script only evaluates retrieval."
    )

    print("\nQuestion Summary:")

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        extra = ""

        if result.get("rank"):
            extra = f" | Rank {result['rank']}"

        print(
            f"[{status}] Question {result['id']}"
            f"{extra} - {result['reason']}"
        )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
