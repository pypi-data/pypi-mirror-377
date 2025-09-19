"""
TBIntLogger

This service is used to log messages and data to Datadog.
"""

import importlib.metadata as importlib_metadata
import logging
import os
import time
from typing import List, Optional, Tuple

import aiohttp
import requests
from dotenv import load_dotenv
from google.cloud import logging as google_cloud_logging

load_dotenv()

__version__ = importlib_metadata.distribution("tbint-logger").version

# Set up Google Cloud Logging if available
try:
    google_cloud_logging_client = google_cloud_logging.Client()
    google_cloud_logging_client.setup_logging()
# pylint: disable=broad-except
except Exception:
    pass

LOGGER_INSTANCE = logging.getLogger("tbint_logger")
LOG_LEVELS = {
    "debug": 10,
    "info": 20,
    "warn": 30,
    "error": 40,
    "critical": 50,
}
LOG_ENVIRONMENTS = [
    "local",
    "development",
    "staging",
    "production",
]
LOG_LEVEL = os.getenv("LOG_LEVEL", "error").lower()
LOG_ENVIRONMENT = os.getenv("LOG_ENVIRONMENT", "").lower()
LOGGER_INSTANCE.setLevel(LOG_LEVELS.get(LOG_LEVEL, 40))

if LOG_ENVIRONMENT == "local":
    LOGGER_INSTANCE.addHandler(logging.StreamHandler())


# pylint: disable=line-too-long
def recursive_serializer(
    data,
) -> Tuple[None, dict | list | str] | Tuple[str, None] | Tuple[None, None]:
    """
    Serialize the data recursively.
    It can be any object, dict, list, etc.
    1. If data is None, return None
    2. If data is not None, try to convert it to a dictionary
    3. If it fails, return "Error serializing data", None
    4. If it succeeds, return None, dict
    """
    if data is None:
        return None, None
    try:
        if isinstance(data, dict):
            return None, {
                key: recursive_serializer(value)[0]
                or recursive_serializer(value)[1]
                for key, value in data.items()
            }
        if isinstance(data, list):
            return None, [
                recursive_serializer(item)[0] or recursive_serializer(item)[1]
                for item in data
            ]
        if hasattr(data, "__dict__"):
            return None, {
                key: recursive_serializer(value)[0]
                or recursive_serializer(value)[1]
                for key, value in data.__dict__.items()
                if not key.startswith("_")
            }
        return None, str(data)
    # pylint: disable=broad-except
    except Exception:
        return "Error serializing input", None


# pylint: disable=too-few-public-methods too-many-instance-attributes
class LoggerData:
    """
    Data class for TBIntLogger
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        system=None,
        event=None,
        correlation_id=None,
        component=None,
        class_name=None,
        method=None,
        description=None,
        duration_ms=None,
        context=None,
    ):

        self.system = system
        self.event = event
        self.correlation_id = correlation_id
        self.component = component
        self.class_name = class_name
        self.method = method
        self.description = description
        self.duration_ms = duration_ms
        self.context = context

    def to_dict(self):
        """
        Convert the data to a dictionary
        """

        ctx_error, ctx_serialized = recursive_serializer(self.context)

        if ctx_error is not None:
            logging.warning("Error serializing context: %s", self.context)

        return {
            "system": self.system,
            "event": self.event,
            "correlation_id": self.correlation_id,
            "component": self.component,
            "class_name": self.class_name,
            "method": self.method,
            "description": self.description,
            "duration_ms": self.duration_ms,
            "context": ctx_serialized,
        }


class Logger:
    """
    Logging service

    This service is used to log messages and data to Datadog.
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        project: Optional[str] = None,
        service: Optional[str] = None,
        system: Optional[str] = None,
        component: Optional[str] = None,
        obfuscate_context_fields: Optional[List[str]] = None,
        obfuscate_context_character="*",
        class_name: Optional[str] = None,
    ):
        self.service: str = service or os.getenv(
            "GCP_SERVICE", os.getenv("DATADOG_SERVICE_NAME", "")
        )
        self.project = project
        self.system = system
        self.component = component
        self.class_name = class_name
        self.obfuscate_context_fields = {
            field.lower() for field in (obfuscate_context_fields or [])
        }
        self.obfuscate_context_character = obfuscate_context_character

        if LOG_ENVIRONMENT not in LOG_ENVIRONMENTS:
            LOGGER_INSTANCE.critical(
                self.get_log_message(
                    "critical",
                    LoggerData(
                        description=f"Invalid LOG_ENVIRONMENT: {LOG_ENVIRONMENT}. Must be one of {LOG_ENVIRONMENTS} Logging won't work."
                    ),
                )
            )
        if LOG_LEVEL not in LOG_LEVELS:
            LOGGER_INSTANCE.critical(
                self.get_log_message(
                    "critical",
                    LoggerData(
                        description=f"Invalid LOG_LEVEL: {LOG_LEVEL}. Must be one of {list(LOG_LEVELS.keys())} Logging won't work."
                    ),
                )
            )

        self.dd_source: str = f"tbint-logger-py/{__version__}"
        self.dd_tags: str = os.getenv("DATADOG_TAGS", os.getenv("DD_TAGS", ""))
        self.dd_api_endpoint: str = os.getenv(
            "DATADOG_API_ENDPOINT",
            os.getenv(
                "DD_API_ENDPOINT",
                "https://http-intake.logs.datadoghq.eu/api/v2/logs",
            ),
        )
        self.dd_api_key: str = os.getenv(
            "DATADOG_API_KEY", os.getenv("DD_API_KEY", "")
        )

    def obfuscate_context(self, context):
        """
        Recursively obfuscate matching fields in the context.
        """
        if isinstance(context, dict):
            return {
                key: (
                    self.obfuscate_context(value)
                    if key.lower() not in self.obfuscate_context_fields
                    else self.obfuscate_context_character * len(str(value))
                )
                for key, value in context.items()
            }
        if isinstance(context, list):
            return [self.obfuscate_context(item) for item in context]
        return context

    def __request_sync(self, headers, log_message):
        if self.dd_api_endpoint != "" and self.dd_api_key != "":
            try:
                response = requests.post(
                    url=self.dd_api_endpoint,
                    json=log_message,
                    headers=headers,
                    timeout=5,
                )
                if not str(response.status_code).startswith("2"):
                    log_res = response.json()
                    LOGGER_INSTANCE.warning(
                        "Error logging: %s %s %s",
                        response.status_code,
                        response.reason,
                        log_res,
                    )
            # pylint: disable=broad-except
            except Exception as e:
                LOGGER_INSTANCE.warning("Error sending log to DataDog: %s", e)

    async def __request_async(self, headers, log_message):
        if self.dd_api_endpoint != "" and self.dd_api_key != "":
            try:
                session = aiohttp.ClientSession()
                response = await session.post(
                    url=self.dd_api_endpoint,
                    json=log_message,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                )
                await session.close()
                if not str(response.status).startswith("2"):
                    log_res = await response.json()
                    LOGGER_INSTANCE.warning(
                        "Error logging: %s %s %s",
                        response.status,
                        response.reason,
                        log_res,
                    )
            # pylint: disable=broad-except
            except Exception as e:
                LOGGER_INSTANCE.warning("Error sending log to DataDog: %s", e)

    def get_headers(self):
        """
        Get headers for the request

        Simple helper function to get the headers for the request
        """

        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "DD-API-KEY": self.dd_api_key,
        }

    def get_log_message(self, level, d: LoggerData) -> dict:
        """
        Get log message

        Simple helper function to get the log message formatted for Datadog
        """

        data = d.to_dict()

        # Fallback to the class attributes if not provided in the data
        project = (
            self.project
            if not data.get("project", None)
            else data.get("project", None)
        )
        service = (
            self.service
            if not data.get("service", None)
            else data.get("service", None)
        )
        system = (
            self.system
            if not data.get("system", None)
            else data.get("system", None)
        )
        component = (
            self.component
            if not data.get("component", None)
            else data.get("component", None)
        )
        class_name = (
            self.class_name
            if not data.get("class_name", None)
            else data.get("class_name", None)
        )

        obfuscated_context = self.obfuscate_context(data.get("context", {}))

        return {
            "project": project,
            "service": service,
            "ddsource": self.dd_source,
            "ddtags": self.dd_tags,
            "level": level,
            "message": {
                # ISO 8601 timestamp
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "env": LOG_ENVIRONMENT,
                "system": system,
                "event": data.get("event", None),
                "correlation_id": data.get("correlation_id", None),
                "component": component,
                "class": class_name,
                "method": data.get("method", None),
                "description": data.get("description", None),
                "duration_ms": data.get("duration_ms", None),
                "context": obfuscated_context,
            },
        }

    async def __log_async(self, level, data):
        if self.should_log(level):
            headers = self.get_headers()
            log_message = self.get_log_message(level, data)
            getattr(LOGGER_INSTANCE, level)(log_message)
            await self.__request_async(headers, log_message)

    def __log_sync(self, level, data):
        if self.should_log(level):
            headers = self.get_headers()
            log_message = self.get_log_message(level, data)
            getattr(LOGGER_INSTANCE, level)(log_message)
            self.__request_sync(headers, log_message)

    def should_log(self, level):
        """
        Check if the message should be logged based on the log level.
        """
        if LOG_ENVIRONMENT not in LOG_ENVIRONMENTS:
            LOGGER_INSTANCE.critical(
                self.get_log_message(
                    "critical",
                    LoggerData(
                        description=f"Invalid LOG_ENVIRONMENT: {LOG_ENVIRONMENT}. Must be one of {LOG_ENVIRONMENTS} Logging won't work."
                    ),
                )
            )
            return False
        if LOG_LEVEL not in LOG_LEVELS:
            LOGGER_INSTANCE.critical(
                self.get_log_message(
                    "critical",
                    LoggerData(
                        description=f"Invalid LOG_LEVEL: {LOG_LEVEL}. Must be one of {list(LOG_LEVELS.keys())} Logging won't work."
                    ),
                )
            )
            return False
        return LOG_LEVELS[level] >= LOG_LEVELS[LOG_LEVEL]

    async def debug(self, data: LoggerData):
        """
        Logs a message and data (debug level) asynchronously
        """
        await self.__log_async("debug", data)

    async def info(self, data: LoggerData):
        """
        Logs a message and data (info level) asynchronously
        """
        await self.__log_async("info", data)

    async def warn(self, data: LoggerData):
        """
        Logs a message and data (warn level) asynchronously
        """
        await self.__log_async("warn", data)

    async def error(self, data: LoggerData):
        """
        Logs a message and data (error level) asynchronously
        """
        await self.__log_async("error", data)

    def debug_sync(self, data: LoggerData):
        """
        Logs a message and data (debug level) synchronously
        """
        self.__log_sync("debug", data)

    def info_sync(self, data: LoggerData):
        """
        Logs a message and data (info level) synchronously
        """
        self.__log_sync("info", data)

    def warn_sync(self, data: LoggerData):
        """
        Logs a message and data (warn level) synchronously
        """
        self.__log_sync("warn", data)

    def error_sync(self, data: LoggerData):
        """
        Logs a message and data (error level) synchronously
        """
        self.__log_sync("error", data)
