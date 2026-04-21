# cloudglue/client/resources/data_connectors.py
"""Data Connectors resource for Cloudglue API."""
from typing import Optional

from cloudglue.sdk.rest import ApiException

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

        Returns URIs compatible with Cloudglue's file import system.
        Supports pagination and provider-specific filtering.

        Args:
            connector_id: The ID of the data connector.
            limit: Maximum number of files to return (1-100, default 20).
            page_token: Opaque cursor for pagination from a previous response.
            var_from: Start date for filtering (YYYY-MM-DD). Zoom and Grain connectors only.
            to: End date for filtering (YYYY-MM-DD). Zoom and Grain connectors only.
            folder_id: Google Drive folder ID. Google Drive connectors only.
            path: Dropbox folder path (default: root). Dropbox connectors only.
            bucket: Bucket name. Required for S3 and GCS connectors.
            prefix: Key prefix filter. S3 and GCS connectors only.
            title_search: Title search filter. Grain connectors only.
            team: Team filter. Grain connectors only.
            meeting_type: Meeting type filter. Grain connectors only.

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
