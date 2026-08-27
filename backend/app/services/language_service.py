from typing import Any

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from app.config import get_settings


class LanguageService:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.language_endpoint or not settings.language_key:
            raise RuntimeError(
                "LANGUAGE_ENDPOINT and LANGUAGE_KEY must be configured in .env."
            )

        self.client = TextAnalyticsClient(
            endpoint=settings.language_endpoint,
            credential=AzureKeyCredential(settings.language_key),
        )

    @staticmethod
    def _get_successful_result(result: Any) -> Any:
        if result.is_error:
            raise RuntimeError(f"Language analysis failed: {result.error}")
        return result

    def analyze_text(self, text: str) -> dict[str, Any]:
        # Azure Language requests have input limits. This project chunks documents later;
        # this first learning example processes a short synthetic document.
        source_text = text[:5000]

        language = self._get_successful_result(
            self.client.detect_language([source_text])[0]
        )
        key_phrases = self._get_successful_result(
            self.client.extract_key_phrases([source_text])[0]
        )
        entities = self._get_successful_result(
            self.client.recognize_entities([source_text])[0]
        )
        pii = self._get_successful_result(
            self.client.recognize_pii_entities([source_text])[0]
        )

        return {
            "detected_language": language.primary_language.iso6391_name,
            "key_phrases": key_phrases.key_phrases,
            "entities": [
                {
                    "text": entity.text,
                    "category": str(entity.category),
                    "subcategory": str(entity.subcategory) if entity.subcategory else None,
                    "confidence": entity.confidence_score,
                }
                for entity in entities.entities
            ],
            "pii_entities": [
                {
                    "text": entity.text,
                    "category": str(entity.category),
                    "confidence": entity.confidence_score,
                }
                for entity in pii.entities
            ],
            "safe_content": pii.redacted_text,
        }