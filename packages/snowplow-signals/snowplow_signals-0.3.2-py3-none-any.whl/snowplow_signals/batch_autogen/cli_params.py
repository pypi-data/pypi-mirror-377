from enum import Enum
from typing import Optional

import typer
from typing_extensions import Annotated

API_KEY = Annotated[
    str,
    typer.Option(
        help="API key for authentication",
        envvar="SNOWPLOW_API_KEY",
    ),
]

API_KEY_ID = Annotated[
    str,
    typer.Option(
        help="ID of the API key",
        envvar="SNOWPLOW_API_KEY_ID",
    ),
]

API_URL = Annotated[
    str,
    typer.Option(
        help="URL of the API server",
        envvar="SNOWPLOW_API_URL",
    ),
]

CHECK_API = Annotated[
    bool,
    typer.Option(
        help="Whether to check API service health",
        envvar="SNOWPLOW_CHECK_API",
    ),
]

CHECK_AUTH = Annotated[
    bool,
    typer.Option(
        help="Whether to check authentication service",
        envvar="SNOWPLOW_CHECK_AUTH",
    ),
]


ORG_ID = Annotated[
    str,
    typer.Option(
        help="Organization ID",
        envvar="SNOWPLOW_ORG_ID",
    ),
]

PROJECT_NAME = Annotated[
    Optional[str],
    typer.Option(
        help="Optional name of a specific project to generate models for",
        envvar="SNOWPLOW_PROJECT_NAME",
    ),
]


REPO_PATH = Annotated[
    str,
    typer.Option(
        help="Path to the repository for the dbt project(s)",
        envvar="SNOWPLOW_REPO_PATH",
    ),
]


UPDATE = Annotated[
    bool,
    typer.Option(
        help="Whether to update existing files",
        envvar="SNOWPLOW_UPDATE",
    ),
]


VERBOSE = Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        help="Enable verbose output",
        envvar="SNOWPLOW_VERBOSE",
    ),
]


ATTRIBUTE_GROUP_NAME = Annotated[
    Optional[str],
    typer.Option(
        help="Name of a specific attribute group",
        envvar="SNOWPLOW_ATTRIBUTE_GROUP_NAME",
    ),
]

ATTRIBUTE_GROUP_VERSION = Annotated[
    Optional[int],
    typer.Option(
        help="Version of the attribute group",
        envvar="SNOWPLOW_ATTRIBUTE_GROUP_VERSION",
    ),
]


class TargetType(str, Enum):
    snowflake = "snowflake"
    bigquery = "bigquery"


TARGET_TYPE = Annotated[
    TargetType,
    typer.Option(
        help="Target database type. One of: `snowflake` or `bigquery`. Default: snowflake",
        envvar="SNOWPLOW_TARGET_TYPE",
    ),
]
