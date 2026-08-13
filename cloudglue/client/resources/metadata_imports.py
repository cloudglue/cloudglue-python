# cloudglue/client/resources/metadata_imports.py
"""Metadata imports resource for Cloudglue API."""
from typing import Any, Dict, List, Optional, Union

from cloudglue.sdk.models.create_metadata_import_request import CreateMetadataImportRequest
from cloudglue.sdk.models.create_metadata_import_run_request import CreateMetadataImportRunRequest
from cloudglue.sdk.models.metadata_import_filter_set import MetadataImportFilterSet
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class MetadataImports:
    """Handles bulk metadata imports for metadata collections.

    A metadata import is a saved definition that lists a data connector's
    source files and imports each one's source metadata into a metadata
    collection as collection files — no media download or processing, and
    runs consume no credits.
    """

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        collection_id: str,
        name: str,
        connector_id: str,
        filters: Optional[List[Union[MetadataImportFilterSet, Dict[str, Any]]]] = None,
        default_mode: Optional[str] = None,
        delete_missing: Optional[bool] = None,
        rate_limit: Optional[int] = None,
        start: Optional[bool] = None,
        max_files: Optional[int] = None,
        include_thumbnails: Optional[bool] = None,
    ):
        """Create a bulk metadata import for a metadata collection.

        By default the first run starts immediately; pass ``start=False`` to
        save the definition only. The response's ``latest_run`` is the
        triggered run; it is None when ``start`` is False or when another
        import's run currently holds the one-active-run-per-collection slot,
        and has status 'failed' when the run could not be enqueued. Runs page
        the connector with the account's default active API key and fail with
        a clear error when the account has none.

        Args:
            collection_id: The ID of the metadata collection.
            name: Display name for the import.
            connector_id: Data connector to list files from. Supported types:
                google-drive, dropbox, zoom, gong, recall, grain, iconik.
            filters: Optional listing passes (each a MetadataImportFilterSet
                or dict): 'from'/'to' date window (YYYY-MM-DD, UTC),
                'title_search', 'folder_id' (Google Drive only), 'path'
                (Dropbox only — non-recursive, direct children), 'team' /
                'meeting_type' (Grain only). Empty or omitted means one
                unfiltered pass; overlapping passes are deduplicated.
            default_mode: Mode used when a run does not specify one: 'append'
                (default — import new files and retry previously-failed ones)
                or 'refresh' (re-import everything the filters match).
            delete_missing: On refresh runs, remove files this import
                previously brought in that the source no longer returns. Only
                files imported by this import are ever removed — never other
                imports', other connectors', or manually added files.
            rate_limit: Upstream list requests per second. Defaults to a
                per-connector safe rate (e.g. gong 2, zoom 6,
                google-drive/dropbox 8) and is clamped to a per-connector
                ceiling at run time.
            start: Trigger the first run immediately (API default True).
                False saves the definition only.
            max_files: Stop each run after processing this many files from
                the listing. A capped run stops listing at the limit and
                never runs the delete-missing sweep.
            include_thumbnails: Copy connector poster images as default
                thumbnails for imported files, for sources that provide one
                (Grain and iconik today). Off by default.

        Returns:
            MetadataImportDetail object (definition plus its latest run).

        Raises:
            CloudglueError: If there is an error creating the import.
        """
        try:
            request = CreateMetadataImportRequest(
                name=name,
                connector_id=connector_id,
                filters=filters,
                default_mode=default_mode,
                delete_missing=delete_missing,
                rate_limit=rate_limit,
                start=start,
                max_files=max_files,
                include_thumbnails=include_thumbnails,
            )
            return self.api.create_metadata_import(
                collection_id=collection_id,
                create_metadata_import_request=request,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List a collection's metadata imports, newest first, each with its
        latest run inline.

        Args:
            collection_id: The ID of the metadata collection.
            limit: Maximum number of imports to return (default 50, max 100).
            offset: Number of imports to skip.

        Returns:
            MetadataImportList object.

        Raises:
            CloudglueError: If there is an error listing imports.
        """
        try:
            return self.api.list_metadata_imports(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(
        self,
        collection_id: str,
        import_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """Get a metadata import definition with one page of its run history
        (newest first).

        Args:
            collection_id: The ID of the metadata collection.
            import_id: The ID of the metadata import.
            limit: Maximum number of runs to return (default 20).
            offset: Number of runs to skip.

        Returns:
            MetadataImportDetail object.

        Raises:
            CloudglueError: If there is an error retrieving the import.
        """
        try:
            return self.api.get_metadata_import(
                collection_id=collection_id,
                import_id=import_id,
                limit=limit,
                offset=offset,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, collection_id: str, import_id: str):
        """Delete a metadata import definition.

        Files the import brought into the collection are not removed.

        Args:
            collection_id: The ID of the metadata collection.
            import_id: The ID of the metadata import.

        Returns:
            MetadataImportDelete confirmation.

        Raises:
            CloudglueError: If there is an error deleting the import.
        """
        try:
            return self.api.delete_metadata_import(
                collection_id=collection_id,
                import_id=import_id,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def run(
        self,
        collection_id: str,
        import_id: str,
        mode: Optional[str] = None,
        delete_missing: Optional[bool] = None,
        max_files: Optional[int] = None,
        include_thumbnails: Optional[bool] = None,
    ):
        """Trigger a new run of a saved import.

        ``mode`` and ``delete_missing`` default to the definition's saved
        values. Only one run may be active per collection at a time;
        triggering while any run in the collection is active raises a
        CloudglueError with status 409.

        Args:
            collection_id: The ID of the metadata collection.
            import_id: The ID of the metadata import.
            mode: 'append' or 'refresh'; defaults to the definition's
                default_mode.
            delete_missing: Override the definition's delete-missing behavior
                for this run (refresh runs only).
            max_files: Override the definition's max_files for this run.
            include_thumbnails: Override the definition's include_thumbnails
                for this run.

        Returns:
            MetadataImportRun object.

        Raises:
            CloudglueError: If there is an error triggering the run (409 when
                a run is already active in the collection).
        """
        try:
            request = CreateMetadataImportRunRequest(
                mode=mode,
                delete_missing=delete_missing,
                max_files=max_files,
                include_thumbnails=include_thumbnails,
            )
            return self.api.create_metadata_import_run(
                collection_id=collection_id,
                import_id=import_id,
                create_metadata_import_run_request=request,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def cancel_run(self, collection_id: str, import_id: str, run_id: str):
        """Cancel an active metadata import run.

        Files already imported by the run stay in the collection; the run is
        settled and marked cancelled.

        Args:
            collection_id: The ID of the metadata collection.
            import_id: The ID of the metadata import.
            run_id: The ID of the run to cancel.

        Returns:
            MetadataImportRun object with its post-cancel status.

        Raises:
            CloudglueError: If there is an error cancelling the run.
        """
        try:
            return self.api.cancel_metadata_import_run(
                collection_id=collection_id,
                import_id=import_id,
                run_id=run_id,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))
