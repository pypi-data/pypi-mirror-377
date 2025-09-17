from __future__ import annotations

import os
from contextlib import contextmanager
from functools import cached_property
from tempfile import NamedTemporaryFile
from typing import Any, Iterator
from urllib.parse import urlparse, urlunparse

from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from universal_transfer_operator.constants import FileLocation, Location, TransferMode
from universal_transfer_operator.data_providers.filesystem.base import (
    BaseFilesystemProviders,
    Path,
    TempFile,
)
from universal_transfer_operator.datasets.file.base import File
from universal_transfer_operator.exceptions import DatabaseCustomError
from universal_transfer_operator.integrations.base import TransferIntegrationOptions


class S3DataProvider(BaseFilesystemProviders):
    """
    DataProviders interactions with S3 Dataset.
    """

    location_type = FileLocation.S3

    def __init__(
        self,
        dataset: File,
        transfer_params: TransferIntegrationOptions = TransferIntegrationOptions(),
        transfer_mode: TransferMode = TransferMode.NONNATIVE,
    ):
        super().__init__(
            dataset=dataset,
            transfer_params=transfer_params,
            transfer_mode=transfer_mode,
        )
        self.transfer_mapping: set = {
            Location.S3,
            Location.GS,
        }

    @cached_property
    def hook(self) -> S3Hook:
        """Return an instance of the database-specific Airflow hook."""
        return S3Hook(
            aws_conn_id=self.dataset.conn_id,
            verify=self.verify,
            transfer_config_args=self.transfer_config_args,
            extra_args=self.s3_extra_args,
        )

    def delete(self, path: str | None = None):
        """
        Delete a file/object if they exists
        """
        path = self.dataset.path if path is None else path
        url = urlparse(path)
        self.hook.delete_objects(bucket=url.netloc, keys=url.path.lstrip("/"))

    @property
    def transport_params(self) -> dict:
        """Structure s3fs credentials from Airflow connection.
        s3fs enables pandas to write to s3
        """
        return {"client": self.hook.conn}

    @property
    def paths(self) -> list[str]:
        """Resolve S3 file paths with prefix"""
        url = urlparse(self.dataset.path)
        prefixes = self.hook.list_keys(
            bucket_name=self.bucket_name,
            prefix=self.s3_key,
            delimiter=self.delimiter,
        )
        paths = [urlunparse((url.scheme, url.netloc, keys, "", "", "")) for keys in prefixes]
        return paths

    def check_if_exists(self, path: str | None = None) -> Any:
        """Return true if the dataset exists"""
        path = self.dataset.path if path is None else path
        return self.hook.check_for_key(key=path)

    @contextmanager
    def read_using_hook(self) -> Iterator[list[TempFile]]:
        """Read the file from dataset and write to local file location"""
        if not self.check_if_exists():
            raise ValueError(f"{self.dataset.path} doesn't exits")
        files = self.hook.list_keys(
            bucket_name=self.bucket_name,
            prefix=self.s3_key,
            delimiter=self.delimiter,
        )
        local_file_paths = []
        try:
            for file in files:
                local_file_paths.append(self.download_file(file))
            yield local_file_paths
        finally:
            # Clean up the local files
            self.cleanup(local_file_paths)

    def write_using_hook(self, source_ref: list[TempFile]):
        """Write the file from local file location to the dataset"""

        dest_s3_key = self.dataset.path

        if not self.keep_directory_structure and self.prefix:
            dest_s3_key = os.path.join(dest_s3_key, self.prefix)

        destination_keys = []
        for file in source_ref:
            if file.tmp_file and file.tmp_file.exists():
                dest_key = os.path.join(dest_s3_key, os.path.basename(file.actual_filename.name))
                self.hook.load_file(
                    filename=file.tmp_file.as_posix(),
                    key=dest_key,
                    replace=True,
                    acl_policy=self.s3_acl_policy,
                )
                destination_keys.append(dest_key)

        return destination_keys

    def download_file(self, file) -> TempFile:
        """Download file and save to temporary path."""
        file_object = self.hook.get_key(file, self.bucket_name)
        _, _, file_name = file.rpartition("/")
        with NamedTemporaryFile(suffix=file_name, delete=False) as tmp_file:
            file_object.download_fileobj(tmp_file)
            return TempFile(tmp_file=Path(tmp_file.name), actual_filename=Path(file_name))

    @property
    def verify(self) -> Any:
        return self.dataset.extra.get("verify")

    @property
    def transfer_config_args(self) -> Any:
        return self.dataset.extra.get("transfer_config_args", {})

    @property
    def s3_extra_args(self) -> Any:
        return self.dataset.extra.get("s3_extra_args", {})

    @property
    def bucket_name(self) -> Any:
        bucket_name, _ = self.hook.parse_s3_url(self.dataset.path)
        return bucket_name

    @property
    def s3_key(self) -> Any:
        _, key = self.hook.parse_s3_url(self.dataset.path)
        return key

    @property
    def s3_acl_policy(self) -> Any:
        return self.dataset.extra.get("s3_acl_policy", None)

    @property
    def prefix(self) -> Any:
        return self.dataset.extra.get("prefix", None)

    @property
    def keep_directory_structure(self) -> Any:
        return self.dataset.extra.get("keep_directory_structure", False)

    @property
    def delimiter(self) -> Any:
        return self.dataset.extra.get("delimiter", None)

    @property
    def openlineage_dataset_namespace(self) -> str:
        """
        Returns the open lineage dataset namespace as per
        https://github.com/OpenLineage/OpenLineage/blob/main/spec/Naming.md
        """
        raise NotImplementedError

    @property
    def openlineage_dataset_name(self) -> str:
        """
        Returns the open lineage dataset name as per
        https://github.com/OpenLineage/OpenLineage/blob/main/spec/Naming.md
        """
        raise NotImplementedError

    @property
    def openlineage_dataset_uri(self) -> str:
        """
        Returns the open lineage dataset uri as per
        https://github.com/OpenLineage/OpenLineage/blob/main/spec/Naming.md
        """
        raise NotImplementedError

    @property
    def size(self) -> int:
        """Return file size for S3 location"""
        url = urlparse(self.dataset.path)
        bucket_name = url.netloc
        object_name = url.path
        if object_name.startswith("/"):
            object_name = object_name[1:]
        obj = self.hook.head_object(key=object_name, bucket_name=bucket_name)
        return obj.get("ContentLength") if obj else -1  # type: ignore

    def get_snowflake_stage_auth_sub_statement(self) -> str:
        aws = self.hook.get_credentials()
        if aws.access_key and aws.secret_key:
            auth = f"credentials=(aws_key_id='{aws.access_key}' aws_secret_key='{aws.secret_key}');"
        else:
            raise DatabaseCustomError(
                "In order to create an stage for S3, one of the following is required: "
                "* `storage_integration`"
                "* AWS_KEY_ID and SECRET_KEY_ID"
            )
        return auth
