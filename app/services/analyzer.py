from app.models.schema import ReviewRequest, ReviewResponse
from app.services.llm_service import LLMService
from app.utils.prompt_builder import build_review_prompt


class CodeAnalyzer:

    def __init__(self):
        self.llm_service = LLMService()

    def analyze(self, request: ReviewRequest) -> ReviewResponse:

        prompt = build_review_prompt(request)

        raw_review = self.llm_service.generate_review(prompt)

        review = ReviewResponse.model_validate(raw_review)

        return review