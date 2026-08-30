"""Application Insights telemetry configuration."""

import logging

from azure.monitor.opentelemetry import configure_azure_monitor

from app.config import get_settings

logger = logging.getLogger(__name__)


def configure_telemetry() -> None:
    """Enable Azure Monitor only when a connection string is configured."""
    settings = get_settings()

    if not settings.applicationinsights_connection_string:
        logger.info(
            "Application Insights is disabled because "
            "APPLICATIONINSIGHTS_CONNECTION_STRING is not configured."
        )
        return

    configure_azure_monitor(
        connection_string=settings.applicationinsights_connection_string,
        logger_name="document_intelligence_hub",
        traces_per_second=1.0,
    )

    logger.info("Application Insights telemetry is enabled.")