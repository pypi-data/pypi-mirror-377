from __future__ import annotations

import sys
from enum import Enum

# typing.Literal was only introduced in Python 3.8, and we support Python 3.7
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class Location(Enum):
    LOCAL = "local"
    GS = "gs"  # Google Cloud Storage
    S3 = "s3"  # Amazon S3
    SFTP = "sftp"
    SQLITE = "sqlite"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"

    def __repr__(self):
        return f"{self}"


class FileLocation(Enum):
    # [START filelocation]
    LOCAL = "local"
    GS = "gs"  # Google Cloud Storage
    S3 = "s3"  # Amazon S3
    SFTP = "sftp"
    # [END filelocation]

    def __repr__(self):
        return f"{self}"


class IngestorSupported(Enum):
    # [START transferingestor]
    Fivetran = "fivetran"
    # [END transferingestor]

    def __repr__(self):
        return f"{self}"


class TransferMode(Enum):
    # [START TransferMode]
    NATIVE = "native"
    NONNATIVE = "nonnative"
    THIRDPARTY = "thirdparty"
    # [END TransferMode]

    def __str__(self) -> str:
        return self.value


class FileType(Enum):
    # [START filetypes]
    CSV = "csv"
    JSON = "json"
    NDJSON = "ndjson"
    PARQUET = "parquet"
    # [END filetypes]

    def __repr__(self):
        return f"{self}"


class Database(Enum):
    # [START database]
    SQLITE = "sqlite"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    # [END database]

    def __repr__(self):
        return f"{self}"


class FivetranConnectorSupported(Enum):
    # [START FivetranConnectorSupported]
    S3 = "S3"
    # [END FivetranConnectorSupported]

    def __str__(self) -> str:
        return self.value


class FivetranDestinationSupported(Enum):
    # [START FivetranDestinationSupported]
    SNOWFLAKE = "snowflake"
    # [END FivetranDestinationSupported]

    def __str__(self) -> str:
        return self.value


SUPPORTED_FILE_LOCATIONS = [const.value for const in FileLocation]
SUPPORTED_FILE_TYPES = [const.value for const in FileType]
SUPPORTED_DATABASES = [const.value for const in Database]

# [START LoadExistStrategy]
LoadExistStrategy = Literal["replace", "append"]
# [END LoadExistStrategy]

DEFAULT_CHUNK_SIZE = 1000000
ColumnCapitalization = Literal["upper", "lower", "original"]
DEFAULT_SCHEMA = "tmp_transfers"
IAM_ROLE_ACTIVATION_WAIT_TIME = 60
