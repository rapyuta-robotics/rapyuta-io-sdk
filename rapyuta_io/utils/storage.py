from __future__ import absolute_import

from typing import BinaryIO, Dict, Optional, Union

HeaderValue = Union[str, bytes, bytearray]

class UploadOptions:
    def __init__(
        self,
        signed_url: str,
        headers: Optional[Dict[str, HeaderValue]] = None,
        metadata: Optional[Dict[str, str]] = None,
        max_concurrency: int = 4,
        length: Optional[int] = None,
    ):
        self.signed_url = signed_url
        self.headers: Dict[str, HeaderValue] = {
            k: (v if isinstance(v, (str, bytes, bytearray)) else str(v))
            for k, v in (headers or {}).items()
        }
        self.metadata = metadata or {}
        self.max_concurrency = max_concurrency
        self.length = length


class Azure:
    def __init__(
        self,
        anonymous: bool = False,
        default_access_tier: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 600,
    ):
        self._anonymous = anonymous
        self.default_access_tier = default_access_tier
        self.max_retries = max_retries
        self.timeout = timeout

    def upload(self, reader: BinaryIO, options: UploadOptions) -> None:
        from azure.storage.blob import BlobClient

        if self._anonymous and not options.signed_url:
            raise ValueError("signed_url is required for anonymous client")

        content_settings = self._generate_blob_content_settings(options.headers)

        blob_client = BlobClient.from_blob_url(
            blob_url=options.signed_url,
            retry_total=self.max_retries,
            connection_timeout=self.timeout,
        )

        blob_client.upload_blob(
            data=reader,
            overwrite=True,
            content_settings=content_settings,
            metadata=options.metadata if options.metadata else None,
            standard_blob_tier=self.default_access_tier,
            max_concurrency=options.max_concurrency,
            length=options.length,
        )

    @staticmethod
    def _generate_blob_content_settings(
        headers: Dict[str, HeaderValue]
    ):
        from azure.storage.blob import ContentSettings

        return ContentSettings(
            content_type=headers.get("x-ms-blob-content-type"),
            content_disposition=headers.get("x-ms-blob-content-disposition"),
            content_md5=headers.get("x-ms-blob-content-md5"),
            content_encoding=headers.get("x-ms-blob-content-encoding"),
        )


def new_anonymous_azure() -> Azure:
    return Azure(anonymous=True)

