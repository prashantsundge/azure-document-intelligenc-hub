from dataclasses import dataclass

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

from app.config import get_settings

BLOCK_SEVERITY = 4


class UnsafeContentError(Exception):
    pass


@dataclass
class SafetyDecision:
    allowed: bool
    severities: dict[str, int]


class ContentSafetyService:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.content_safety_endpoint or not settings.content_safety_key:
            raise RuntimeError(
                "CONTENT_SAFETY_ENDPOINT and CONTENT_SAFETY_KEY "
                "must be configured in .env."
            )

        self.client = ContentSafetyClient(
            endpoint=settings.content_safety_endpoint,
            credential=AzureKeyCredential(settings.content_safety_key),
        )

    def evaluate(self, text: str) -> SafetyDecision:
        result = self.client.analyze_text(
            AnalyzeTextOptions(text=text[:10000])
        )

        severities = {
            str(category.category): category.severity
            for category in result.categories_analysis
        }

        return SafetyDecision(
            allowed=all(severity < BLOCK_SEVERITY for severity in severities.values()),
            severities=severities,
        )

    def require_safe(self, text: str, content_type: str) -> None:
        decision = self.evaluate(text)

        if not decision.allowed:
            raise UnsafeContentError(
                f"The {content_type} was blocked by Azure AI Content Safety."
            )