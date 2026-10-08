import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured")


client = genai.Client(
    api_key=api_key
)


response = client.interactions.create(
    model=os.getenv("LLM_MODEL", "gemini-3.8-flash"),
    input="Say hello in one short sentence."
)


print(response.output_text)
