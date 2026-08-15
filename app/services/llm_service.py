import json

from google import genai

from app.core.config import settings


class LLMService:
    def __init__(self):
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is not configured.")

        self.client = genai.Client(api_key=settings.llm_api_key)

    def generate_review(self, prompt: str) -> dict:

        response = self.client.models.generate_content(
            model=settings.llm_model,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )

        try:
            return json.loads(response.text)

        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned an invalid JSON response.") from exc
