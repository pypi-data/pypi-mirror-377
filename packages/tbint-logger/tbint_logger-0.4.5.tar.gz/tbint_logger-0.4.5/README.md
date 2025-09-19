# TBint Logger Python

`TBIntLogger` is a Python-based logging library designed to simplify
logging messages and data to [Datadog](https://www.datadoghq.com/).

It supports both synchronous and asynchronous logging,
providing flexibility for various application needs.

## Features

- Log messages at different levels: `debug`, `info`, `warn`, `error`.
- Support for both synchronous and asynchronous logging.
- Customizable through environment variables.
- Easy integration with Datadog for centralized logging and monitoring.

## Installation

You can install `tbint-logger` from PyPI:

```sh
pip install tbint-logger
```

## Getting started

### Environment variables

Before using `tb-logger`, set the following environment variables:

- `LOG_LEVEL`: The log level threshold (default: `error`). Possible values: `debug`, `info`, `warn`, `error`, `critical`.
- `LOG_ENVIRONMENT`: The logging environment (default: `development`, possible values:  `production`, `staging`, `development`, `local`).

Example `.env` file:

```env
LOG_LEVEL=debug
LOG_ENVIRONMENT=local
```

If you want to enable Datadog logs, you must also set `DATADOG_API_KEY`.
Optionally, you can set `DATADOG_API_ENDPOINT` to use a different Datadog site and
`DATADOG_TAGS` to add tags to your logs.

If you want the service name in Datadog to be different from
the default that's passed to the logger constructor,
you can set `DATADOG_SERVICE_NAME` to the desired value.

Example `.env` file:

```env
LOG_LEVEL=debug
LOG_ENVIRONMENT=local
DATADOG_SERVICE_NAME=my-service
DATADOG_SOURCE=production
DATADOG_TAGS=env:production,team:backend
DATADOG_API_ENDPOINT=https://http-intake.logs.datadoghq.eu/api/v2/logs
DATADOG_API_KEY=your-datadog-api-key
```

### Basic usage

## LoggerData class

The `LoggerData` class is used to structure log messages.
It accepts the following attributes:

| Attribute                     | Type            | Description                                 |
|-------------------------------|-----------------|---------------------------------------------|
| `service`                     | `Optional[str]` | The service generating the log.             |
| `system`                      | `Optional[str]` | The system generating the log.              |
| `project`                     | `Optional[str]` | The project name.                           |
| `component`                   | `Optional[str]` | The system component generating the log.    |
| `class_name`                  | `Optional[str]` | The class name where the log originates.    |
| `obfuscate_context_fields`    | `List[str]`     | List of fields to obfuscate in the context. |
| `obfuscate_context_character` | `Optional[str]` | Character to use for obfuscation.           |


#### Synchronous logging

```python
from tbint_logger import Logger, LoggerData

# Init with default values
logger = Logger(
    system="my-system",
    component="auth",
    class_name="AuthService",
    # NOTE:
    # This will obfuscate the context (list or dict) fields
    # recursively, with the character '*'.
    # Matches are case-insensitive.
    # INFO: This is completely optional.
    obfuscate_context_fields=["password", "email", "cc_number", "cvv"],
    obfuscate_context_character="*"
)

# Default values can be overridden
# on each call to the logger
data = LoggerData(
    system="my-system2",
    event="user-login",
    correlation_id="abc123",
    component="auth2",
    class_name="AuthService2",
    method="login",
    description="User successfully logged in",
    duration_ms=120,
    context={
        "user_id": 42,
        "email": "foo@bar.de",
        "password": "secret",
        "cc_number": "1234567890",
        "cvv": "123"
    }
)

logger.info_sync(data)
```

#### Asynchronous Logging

```python
import asyncio
from tbint_logger import Logger, LoggerData

# Init with default values
logger = Logger(
    system="my-system",
    component="auth",
    class_name="AuthService",
)

# Default values can be overridden
# on each call to the logger
data = LoggerData(
    system="my-system2",
    event="user-login",
    correlation_id="abc123",
    component="auth2",
    class_name="AuthService2",
    method="login",
    description="User successfully logged in",
    duration_ms=120,
    context={"user_id": 42}
)

async def log_event():
    await logger.info(data)

asyncio.run(log_event())
```

### Logging Levels

- **Debug**: Use for detailed diagnostic information.
  ```python
  logger.debug_sync(data)
  await logger.debug(data)
  ```

- **Info**: Use for general informational messages.
  ```python
  logger.info_sync(data)
  await logger.info(data)
  ```

- **Warn**: Use for warnings that don't require immediate attention.
  ```python
  logger.warn_sync(data)
  await logger.warn(data)
  ```

- **Error**: Use for errors that require attention.
  ```python
  logger.error_sync(data)
  await logger.error(data)
  ```

- **Critical**: Use for critical issues that need immediate attention.
  ```python
  logger.critical_sync(data)
  await logger.critical(data)
  ```

## LoggerData Class

The `LoggerData` class is used to structure log messages.
It accepts the following attributes:

| Attribute        | Type   | Description                                       |
|------------------|--------|---------------------------------------------------|
| `system`         | `str`  | The system generating the log.                    |
| `project`        | `str`  | The project name (optional).                      |
| `event`          | `str`  | The event type (e.g., "user-login").              |
| `correlation_id` | `str`  | A unique identifier for correlating logs.         |
| `component`      | `str`  | The system component generating the log.          |
| `class_name`     | `str`  | The class name where the log originates.          |
| `method`         | `str`  | The method where the log originates.              |
| `description`    | `str`  | A description of the log event.                   |
| `duration_ms`    | `int`  | Duration of the event in milliseconds.            |
| `context`        | `dict` | Additional context data to include in the log.    |

## How It Works

1. **Environment Configuration**: Reads environment variables for Datadog configuration.
2. **Log Message Construction**: Formats log messages with metadata and timestamp.
3. **Datadog Integration**: Sends logs to Datadog via API.
4. **Sync/Async Options**: Offers both synchronous and asynchronous logging for flexible use cases.

## License

`tb-logger` is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.


## Development

```sh
python3 -m venv venv
source venv/bin/activate
rm -rf dist/*
python3 -m pip install -r requirements.txt
python3 -m build
python3 -m twine upload --repository pypi dist/*
```

## Update Requirements

```sh
python3 -m pip freeze > requirements.txt
```
