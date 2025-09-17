import json
from contextlib import redirect_stdout
from io import StringIO

import structlog

from structlog_cloudrun import CloudRunProcessor


def test_full_pipeline_with_json_renderer():
    """Test complete pipeline ending with JSON output."""
    output_stream = StringIO()

    # Configure structlog with CloudRunProcessor
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            CloudRunProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()

    # Capture output
    with redirect_stdout(output_stream):
        logger.info("User logged in", user_id="12345", method="oauth")

    output = output_stream.getvalue().strip()

    log_data = json.loads(output)

    # Verify Cloud Run log format
    assert "severity" in log_data
    assert "message" in log_data

    assert log_data["severity"] == "INFO"
    assert log_data["message"] == "User logged in"
    assert log_data["user_id"] == "12345"
    assert log_data["method"] == "oauth"
