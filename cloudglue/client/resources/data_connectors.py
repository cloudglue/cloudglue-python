# cloudglue/client/resources/data_connectors.py
"""Data Connectors resource for Cloudglue API."""
from typing import Optional

from cloudglue.sdk.rest import ApiException
from cloudglue.sdk.models.sync_data_connector_file_request import (
    SyncDataConnectorFileRequest,
)

from cloudglue.client.resources.base import CloudglueError


class DataConnectors:
    """Client for the Cloudglue Data Connectors API."""

    def __init__(self, api):
        """Initialize the DataConnectors client.

        Args:
            api: The DataConnectorsApi instance.
        """
        self.api = api

    def list(self):
        """List all active data connectors configured for your account.

        Returns:
            DataConnectorList object

        Raises:
            CloudglueError: If there is an error listing data connectors.
        """
        try:
            return self.api.list_data_connectors()
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_files(
        self,
        connector_id: str,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        var_from: Optional[str] = None,
        to: Optional[str] = None,
        folder_id: Optional[str] = None,
        path: Optional[str] = None,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
        title_search: Optional[str] = None,
        team: Optional[str] = None,
        meeting_type: Optional[str] = None,
    ):
        """Browse files available in a connected data source.

        Returns URIs compatible with Cloudglue's file import system, plus
        per-file provider metadata (the `metadata` field) so you can inspect
        participants, hosts, durations, and AI summaries before importing.

        Supports pagination and filtering; parameters a connector can't honor
        are silently ignored. When filters are applied, a page may contain
        fewer than `limit` items — even zero — while `has_more` is still
        true: keep paginating until `next_page_token` is None rather than
        stopping at the first short or empty page.

        Args:
            connector_id: The ID of the data connector.
            limit: Maximum number of files to return (1-100).
            page_token: Opaque cursor for pagination. Use the `next_page_token`
                from a previous response. Tokens are only valid with the same
                filter parameters they were issued under.
            var_from: Start date for filtering (YYYY-MM-DD, inclusive UTC day
                bound). Supported by Grain, Zoom, Recall, Google Drive,
                Dropbox, and Gong (Zoom and Gong default to a 6-month lookback
                when omitted); ignored for S3/GCS.
            to: End date for filtering (YYYY-MM-DD). Same per-connector
                support as `var_from`.
            folder_id: Google Drive folder ID to list contents of. Applies to Google Drive connectors only.
            path: Dropbox folder path to list contents of (default: root). Applies to Dropbox connectors only.
            bucket: Bucket name. Required for S3 and GCS connectors.
            prefix: Key prefix filter. Applies to S3 and GCS connectors only.
            title_search: Case-insensitive title filter. Supported by Grain,
                Zoom, Google Drive, Dropbox, and Gong; ignored for Recall (no
                title is available when listing) and S3/GCS.
            team: Team filter. Applies to Grain connectors only. See the [Grain documentation](https://developers.grain.com/#recording-filter) for more details.
            meeting_type: Meeting type filter. Applies to Grain connectors only. See the [Grain documentation](https://developers.grain.com/#recording-filter) for more details.

        Returns:
            DataConnectorFileList object.

        Raises:
            CloudglueError: If there is an error listing data connector files.
        """
        try:
            return self.api.list_data_connector_files(
                id=connector_id,
                limit=limit,
                page_token=page_token,
                var_from=var_from,
                to=to,
                folder_id=folder_id,
                path=path,
                bucket=bucket,
                prefix=prefix,
                title_search=title_search,
                team=team,
                meeting_type=meeting_type,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_source_metadata(self, connector_id: str, url: str):
        """Look up source metadata for a connector URI.

        Returns provider-specific metadata (recording/call/file details) for a
        single file in a connected data source, without importing it.

        Supported for Grain, Zoom, Recall, Google Drive, Dropbox, and Gong
        connectors. S3/GCS raise a CloudglueError with status 501 (plain
        object stores have no richer metadata); a 502 is raised when the
        upstream provider's response can't be validated.

        Args:
            connector_id: The ID of the data connector.
            url: Connector URI to look up. Must match the connector's type.

        Returns:
            SourceMetadataResponse object. `source_metadata` holds the
            provider's metadata, discriminated by its `source_type` field.

        Raises:
            CloudglueError: If there is an error fetching source metadata
                (including 501 for S3/GCS connectors).
        """
        try:
            return self.api.get_data_connector_source_metadata(
                id=connector_id,
                url=url,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def sync_file(self, connector_id: str, url: str):
        """Sync a file from a connected data source into Cloudglue.

        Imports the file at the given connector URI, returning the resulting
        Cloudglue file (creating it if it does not already exist). Idempotent:
        syncing the same URI returns the existing file. For Grain, Zoom,
        Recall, Google Drive, Dropbox, and Gong the file's `source_metadata`
        is populated from the provider.

        Besides the connector URIs emitted by `list_files()` (`s3://`,
        `gs://`, `gdrive://file/<id>`, `dropbox://<path>`, `zoom://`,
        `grain://recording/<id>`, ...), the server resolves these share links
        via the connector's OAuth:
            - Google Drive share links (`drive.google.com/file/d/<id>`,
              `/open?id=<id>`)
            - Dropbox file share links (`dropbox.com/scl/fi/...`, `/s/...` —
              works for login-gated files; folder links return 400)
            - Zoom links (`https://*.zoom.us/{j|s|recording/detail|rec/share}`).
              `rec/share` links resolve best-effort: Zoom often mints a new
              share token each time a link is copied, so fresh links may 404 —
              the reliable form is the recording-detail link
              (`zoom.us/recording/detail?meeting_id=<uuid>`).

        Plain http(s), TikTok, and Loom URLs are not connector-syncable —
        ingest those via `files.sync_from_url` instead. YouTube URLs can only
        be added to a collection (`collections.add_media`).

        Args:
            connector_id: The ID of the data connector.
            url: Connector URI or supported share link to sync. Must match
                the connector's type.

        Returns:
            File object.

        Raises:
            CloudglueError: If there is an error syncing the file (e.g. 400
                for folder links or type mismatches, 403 for inaccessible
                share links, 404 if not found at the source, 429 if the
                external service rate-limited the request).
        """
        try:
            request = SyncDataConnectorFileRequest(url=url)
            return self.api.sync_data_connector_file(
                id=connector_id,
                sync_data_connector_file_request=request,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))
