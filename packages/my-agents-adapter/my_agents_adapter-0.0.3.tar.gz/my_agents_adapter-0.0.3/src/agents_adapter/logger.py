import logging
import os
from logging import config

from .constants import Constants

default_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "container_agents_adapter": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "handlers": {
        "console": {"formatter": "std_out", "class": "logging.StreamHandler", "level": "INFO"},
    },
    "formatters": {"std_out": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
}


class CustomLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None):
        dimensions = get_dimensions()
        if extra:
            dimensions.update(extra)
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra=dimensions)


def get_dimensions():
    agent_id = os.environ.get(Constants.AGENT_ID, "test_agent_id")
    return {
        "agent_id": agent_id,
    }


def get_project_endpoint():
    project_resource_id = os.environ.get(Constants.AGENT_PROJECT_RESOURCE_ID)
    if project_resource_id:
        last_part = project_resource_id.split("/")[-1]

        parts = last_part.split("@")
        if len(parts) < 2:
            print(f"invalid project resource id: {project_resource_id}")
            return None
        account = parts[0]
        project = parts[1]
        return f"https://{account}.services.ai.azure.com/api/projects/{project}"
    else:
        print("environment variable AGENT_PROJECT_RESOURCE_ID not set.")
        return None


def get_application_insights_connection_string():
    try:
        conn_str = os.environ.get(Constants.APPLICATION_INSIGHTS_CONNECTION_STRING)
        if not conn_str:
            print("environment variable APPLICATION_INSIGHTS_CONNECTION_STRING not set.")
            project_endpoint = get_project_endpoint()
            if project_endpoint:
                # try to get the project connected application insights
                from azure.ai.projects import AIProjectClient
                from azure.identity import DefaultAzureCredential

                project_client = AIProjectClient(credential=DefaultAzureCredential(), endpoint=project_endpoint)
                conn_str = project_client.telemetry.get_connection_string()
                if not conn_str:
                    print(f"no connected application insights found for project:{project_endpoint}")
        return conn_str
    except Exception as e:
        print(f"failed to get application insights with error: {e}")
        return None


class CustomDimensionsFilter(logging.Filter):
    def filter(self, record):
        # Add custom dimensions to every log record
        dimensions = get_dimensions()
        for key, value in dimensions.items():
            setattr(record, key, value)
        return True


def configure(log_config: dict = default_log_config):
    """
    Configure logging based on the provided configuration dictionary.
    The dictionary should contain the logging configuration in a format compatible with `logging.config.dictConfig`.
    """
    try:
        logging.setLoggerClass(CustomLogger)

        config.dictConfig(log_config)

        application_insights_connection_string = get_application_insights_connection_string()
        if application_insights_connection_string:
            from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
            from opentelemetry._logs import set_logger_provider
            from opentelemetry.sdk._logs import (
                LoggerProvider,
                LoggingHandler,
            )
            from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
            from opentelemetry.sdk.resources import Resource

            logger_provider = LoggerProvider(resource=Resource.create({"service.name": "agent_runtime.agent_adapter"}))
            set_logger_provider(logger_provider)

            exporter = AzureMonitorLogExporter(connection_string=application_insights_connection_string)

            logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
            handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

            # Add custom filter to inject dimensions
            custom_filter = CustomDimensionsFilter()
            handler.addFilter(custom_filter)

            # Only add to container_agents_adapter namespace to avoid infrastructure logs
            app_logger = logging.getLogger("container_agents_adapter")
            app_logger.setLevel(logging.DEBUG)
            app_logger.addHandler(handler)

    except Exception as e:
        print(f"Failed to configure logging: {e}")
        pass


def get_logger():
    """
    If the logger is not already configured, it will be initialized with default settings.
    """
    return logging.getLogger("container_agents_adapter")
