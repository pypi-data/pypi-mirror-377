import pytest
from structlog_cloudrun import CloudRunProcessor, Severity


processor = CloudRunProcessor()


@pytest.fixture
def event_dict() -> dict:
    """Provide a sample event dictionary for testing."""
    return {
        "event": "Test log message",
        "user_id": "12345",
        "action": "login",
        "extra_data": {"key": "value"},
    }


def test_basic_log_processing(event_dict: dict):
    """Test basic log processing with standard input."""
    result = processor(None, "info", event_dict.copy())

    assert isinstance(result, dict)
    assert result["severity"] == Severity.INFO
    assert result["message"] == "Test log message"
    assert "event" not in result

    assert result == {
        "severity": Severity.INFO,
        "message": "Test log message",
        "user_id": "12345",
        "action": "login",
        "extra_data": {"key": "value"},
    }


def test_severity_mapping():
    """Test severity mapping for different log levels."""
    test_cases = [
        ("notset", Severity.DEFAULT),
        ("debug", Severity.DEBUG),
        ("info", Severity.INFO),
        ("warning", Severity.WARNING),
        ("error", Severity.ERROR),
        ("critical", Severity.CRITICAL),
    ]

    for level, expected_severity in test_cases:
        result = processor(None, level, {"event": "test"})
        assert result["severity"] == expected_severity


def test_unknown_log_level():
    """Test handling of unknown log levels defaults to DEFAULT."""
    result = processor(None, "unknown_level", {"event": "test"})
    assert result["severity"] == Severity.DEFAULT


def test_empty_json_payload():
    """Test handling of event dict with only event field."""
    event_dict = {"event": "Simple message"}
    result = processor(None, "info", event_dict)

    assert result["message"] == "Simple message"
    assert result == {
        "severity": Severity.INFO,
        "message": "Simple message",
    }
