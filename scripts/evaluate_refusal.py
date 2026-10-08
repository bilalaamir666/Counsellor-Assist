import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer


QUESTIONS_FILE = PROJECT_ROOT / "eval" / "questions.json"

REFUSAL_TEXT = "I could not find this information in the provided documents."
TIMEOUT_SECONDS = 30


def call_gemini(question, results):
    return generate_answer(
        question,
        results,
        conversation_history=[]
    )


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    unanswerable = [
        q for q in questions
        if q["answerable"] is False
    ]

    print("=" * 80)
    print("COUNSELLOR ASSIST - UNANSWERABLE QUESTION EVALUATION")
    print("=" * 80)
    print(f"Testing {len(unanswerable)} unanswerable questions")
    print(f"Gemini timeout: {TIMEOUT_SECONDS} seconds")

    passed = 0

    for question in unanswerable:
        print("\n" + "=" * 80)
        print(f"Question {question['id']}: {question['question']}")
        print("=" * 80, flush=True)

        try:
            results = search_similar_chunks(
                question["question"],
                limit=5
            )

            print(f"Retrieved {len(results)} chunks", flush=True)

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    call_gemini,
                    question["question"],
                    results
                )

                try:
                    llm_result = future.result(
                        timeout=TIMEOUT_SECONDS
                    )
                except TimeoutError:
                    print(
                        f"\nTIMEOUT - Gemini did not respond within "
                        f"{TIMEOUT_SECONDS} seconds"
                    )
                    continue

            answer = llm_result["answer"]
            supporting_chunks = llm_result["supporting_chunks"]

            print(f"\nAnswer: {answer}")
            print(f"Supporting chunks: {supporting_chunks}")

            if (
                answer.strip() == REFUSAL_TEXT
                and supporting_chunks == []
            ):
                print("\nPASS - Correct refusal")
                passed += 1
            else:
                print("\nFAIL - Incorrect refusal")

        except Exception as e:
            print(f"\nERROR - {type(e).__name__}: {e}")

    print("\n" + "=" * 80)
    print("FINAL REFUSAL EVALUATION")
    print("=" * 80)

    failed = len(unanswerable) - passed

    print(f"Passed: {passed}/{len(unanswerable)}")
    print(f"Failed: {failed}/{len(unanswerable)}")

    if unanswerable:
        print(
            f"Refusal accuracy: "
            f"{(passed / len(unanswerable)) * 100:.2f}%"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
