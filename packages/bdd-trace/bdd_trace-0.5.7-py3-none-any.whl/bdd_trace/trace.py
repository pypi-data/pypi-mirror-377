import logging
import os
from enum import Enum

from opentelemetry.instrumentation import auto_instrumentation


class Profile(str, Enum):
    NO_TRACE = "no_trace"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


_TRACE_PROFILE_KEY = "BDD_TRACE_PROFILE"
_TRACES_EXPORTER_KEY = "traces_exporter"
_METRICS_EXPORTER_KEY = "metrics_exporter"
_LOGS_EXPORTER_KEY = "logs_exporter"
_EXPORTER_OTLP_ENDPOINT_KEY = "exporter_otlp_endpoint"
_EXPORTER_OTLP_INSECURE_KEY = "exporter_otlp_insecure"
_SERVICE_NAME_KEY = "service_name"
_PYTHON_FASTAPI_EXCLUDE_URLS_KEY = "python_fastapi_excluded_urls"
_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST_KEY = "instrumentation_http_capture_headers_server_request"
_OTEL_PYTHON_LOG_CORRELATION_KEY = "otel_python_log_correlation"
_EXPORTER_OTLP_TRACES_PROTOCOL_KEY = "exporter_otlp_traces_protocol"
_EXPORTER_OTLP_METRICS_PROTOCOL_KEY = "exporter_otlp_metrics_protocol"
_EXPORTER_OTLP_LOGS_PROTOCOL_KEY = "exporter_otlp_logs_protocol"

_default_envs = {
    _TRACES_EXPORTER_KEY: "otlp",
    _METRICS_EXPORTER_KEY: "otlp",
    _LOGS_EXPORTER_KEY: "otlp",
    _PYTHON_FASTAPI_EXCLUDE_URLS_KEY: "/healthCheck",
    _INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST_KEY: "X-User-Id,X-Conversation-From",
    _EXPORTER_OTLP_INSECURE_KEY: "true",
    _OTEL_PYTHON_LOG_CORRELATION_KEY: "true",
}

_profile_config = {
    Profile.DEV: {
        _TRACES_EXPORTER_KEY: "otlp",
        _METRICS_EXPORTER_KEY: "otlp",
        _LOGS_EXPORTER_KEY: "otlp",
        _EXPORTER_OTLP_ENDPOINT_KEY: "http://otel-sls-collector-test.life-science-platform.zhejianglab.com",
        _EXPORTER_OTLP_TRACES_PROTOCOL_KEY: "http/protobuf",
        _EXPORTER_OTLP_METRICS_PROTOCOL_KEY: "http/protobuf",
        _EXPORTER_OTLP_LOGS_PROTOCOL_KEY: "http/protobuf",
    },
    Profile.TEST: {
        _TRACES_EXPORTER_KEY: "otlp",
        _METRICS_EXPORTER_KEY: "otlp",
        _LOGS_EXPORTER_KEY: "otlp",
        _EXPORTER_OTLP_ENDPOINT_KEY: "http://otel-sls-collector:4317",
    },
    Profile.PROD: {
        _TRACES_EXPORTER_KEY: "otlp",
        _METRICS_EXPORTER_KEY: "otlp",
        _LOGS_EXPORTER_KEY: "otlp",
        _EXPORTER_OTLP_ENDPOINT_KEY: "http://otel-sls-collector:4317",
    },
}

logger = logging.getLogger(__name__)


def init_trace(
    *,
    service_name: str | None = None,
    profile: Profile | None = None,
    exporter_otlp_endpoint: str | None = None,
    **kwargs,
) -> None:
    # 设置环境变量，优先级：环境变量 > 参数 > profile 配置 > 默认配置
    for key, value in kwargs.items():
        _set_env(key, value)

    if profile := _get_profile(profile):
        if profile == Profile.NO_TRACE:
            logger.info("NO_TRACE profile is set, skip auto instrumentation")
            return
        for key, value in _profile_config[profile].items():
            _set_env(key, value)
    elif exporter_otlp_endpoint:
        _set_env(_EXPORTER_OTLP_ENDPOINT_KEY, exporter_otlp_endpoint)
    else:
        logger.info("no profile or exporter_otlp_endpoint is set, skip auto instrumentation")
        return

    if service_name:
        _set_env(_SERVICE_NAME_KEY, service_name)
    elif _get_env(_SERVICE_NAME_KEY) is None:
        raise ValueError("service_name is required")

    for key, value in _default_envs.items():
        _set_env(key, value)

    auto_instrumentation.initialize()


def _get_profile(profile: Profile | None) -> Profile | None:
    if profile:
        return profile
    profile_env = os.getenv(_TRACE_PROFILE_KEY)
    if profile_env:
        try:
            return Profile(profile_env)
        except ValueError:
            raise ValueError(f"invalid profile from env {_TRACE_PROFILE_KEY}: {profile_env}")
    return None


def _set_env(key: str, value: str | None) -> None:
    if value is None:
        return

    env_key = _convert_to_env_key(key)
    if existing_value := os.getenv(env_key):
        logger.info(f"existing env {env_key}={existing_value}")
    else:
        logger.debug(f"set env {env_key}={value}")
        os.environ[env_key] = value


def _get_env(key: str) -> str | None:
    env_key = _convert_to_env_key(key)
    return os.getenv(env_key)


def _convert_to_env_key(key: str) -> str:
    return f"OTEL_{key.upper()}"
