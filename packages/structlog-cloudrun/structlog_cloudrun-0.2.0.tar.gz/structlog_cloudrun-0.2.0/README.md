# structlog-cloudrun

A [structlog](https://www.structlog.org/) processor for Google Cloud Run logging.

This package provides a structured logging processor that formats log entries to be compatible with Google Cloud Logging when running on Cloud Run.

## Features

- Converts structlog events to Google Cloud Logging format
- Maps Python log levels to Cloud Logging severity levels
- Automatic UTC timestamp generation
- Separates log messages and structured data appropriately

## Installation

Install using pip:

```bash
pip install structlog-cloudrun
```

Or using uv:

```bash
uv add structlog-cloudrun
```

## Quick Start

```python
import structlog
from structlog_cloudrun import CloudRunProcessor

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

# Use structured logging
logger = structlog.get_logger()
logger.info("User logged in", user_id="12345", method="oauth")
```

This will output JSON formatted for Google Cloud Logging:

```json
{
  "severity": "INFO",
  "timestamp": "2023-12-07T10:30:00.000000Z",
  "textPayload": "User logged in",
  "jsonPayload": {
    "user_id": "12345",
    "method": "oauth"
  }
}
```

## Log Format

The processor converts structlog events into Google Cloud Logging's `LogEntry` format:

- **severity**: Mapped from Python log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **timestamp**: UTC timestamp in ISO format
- **textPayload**: The main log message (from the `event` field)
- **jsonPayload**: All other structured data from the log event

## Severity Mapping

| Python Level | Cloud Logging Severity |
| ------------ | ---------------------- |
| notset       | DEFAULT                |
| debug        | DEBUG                  |
| info         | INFO                   |
| notice       | NOTICE                 |
| warning      | WARNING                |
| error        | ERROR                  |
| critical     | CRITICAL               |

## Requirements

- Python 3.11+
- structlog 25.0.0+
