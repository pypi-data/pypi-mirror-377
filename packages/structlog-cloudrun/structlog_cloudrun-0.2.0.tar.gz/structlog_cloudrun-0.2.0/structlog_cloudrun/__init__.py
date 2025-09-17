from enum import StrEnum
from typing import Any

from structlog.typing import EventDict

from dataclasses import dataclass, asdict


class Severity(StrEnum):
    DEFAULT: str = "DEFAULT"
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    NOTICE: str = "NOTICE"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"
    CRITICAL: str = "CRITICAL"
    ALERT: str = "ALERT"
    EMERGENCY: str = "EMERGENCY"


LEVEL_MAPPING = {
    "notset": Severity.DEFAULT,
    "debug": Severity.DEBUG,
    "info": Severity.INFO,
    "notice": Severity.NOTICE,
    "warn": Severity.WARNING,
    "warning": Severity.WARNING,
    "error": Severity.ERROR,
    "exception": Severity.ERROR,
    "critical": Severity.CRITICAL,
}


class CloudRunProcessor:
    """Processor to convert structlog output to Google Cloud Logging format."""

    def __call__(
        self, logger: Any, method_name: str, event_dict: EventDict
    ) -> EventDict:
        """Convert event_dict for Google Cloud Logging LogEntry."""

        severity = LEVEL_MAPPING.get(method_name, "DEFAULT")
        message = event_dict.pop("event")

        return {
            "severity": severity,
            "message": message,
            **event_dict,
        }
