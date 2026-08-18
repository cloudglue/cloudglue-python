# cloudglue/client/resources/bulk_imports.py
"""Bulk imports resource for Cloudglue API."""
from typing import Any, Dict, List, Optional, Union

from cloudglue.sdk.models.create_metadata_import_request import CreateMetadataImportRequest
from cloudglue.sdk.models.create_metadata_import_run_request import CreateMetadataImportRunRequest
from cloudglue.sdk.models.metadata_import_filter_set import MetadataImportFilterSet
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class BulkImports:
    """Handles bulk imports: batch-importing a data connector's source files
    into a collection from a saved definition.

    What a run ingests follows the collection's type, reported as
    ``import_type`` on the definition and on every run:

    - ``metadata`` (metadata collections): each file's source metadata is
      imported as a collection file. No media is downloaded or processed and
      runs consume no credits.
    - ``media`` (every other collection type): each matching file is ingested
      and processed exactly like a manual add, so it is billed per file and
      counts against the account's file usage limits.
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
        enrich_metadata: Optional[bool] = None,
    ):
        """Create a bulk import.

        ``import_type`` is inferred from the collection's type at creation
        and fixed for the import's lifetime — definitions are immutable, so
        delete and recreate to change one. A metadata collection yields a
        metadata import (source metadata only, free); every other collection
        type yields a media import, which ingests and processes each matching
        file exactly like a manual add and is billed per file.

        By default the first run starts immediately; pass ``start=False`` to
        save the definition only. The response's ``latest_run`` is the
        triggered run; it is None when ``start`` is False or when another run
        is already active in the collection, and has status 'failed' when the
        run could not be started. Runs page the connector — and, for media
        imports, add each file — with the account's default active API key,
        and fail with a clear error when the account has none.

        Args:
            collection_id: The ID of the collection to import into.
            name: Display name for the import.
            connector_id: Data connector to list files from. Supported types:
                google-drive, dropbox, zoom, gong, recall, grain, iconik.
            filters: Optional listing passes (each a MetadataImportFilterSet
                or dict): 'from'/'to' date window (YYYY-MM-DD, UTC),
                'title_search', 'folder_id' (Google Drive only), 'path' and
                'recursive' (Dropbox only — 'path' lists direct children,
                'recursive' set to 'true' lists the whole subtree under it),
                'team' / 'meeting_type' (Grain only). Empty or omitted means
                one unfiltered pass; overlapping passes are deduplicated.
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
                never runs the delete-missing sweep. Media imports are
                additionally capped at 10,000 files per run, whatever this
                is set to.
            include_thumbnails: Copy connector poster images as default
                thumbnails for imported files, for sources that provide one
                (Grain, iconik, Google Drive, and Dropbox today). Off by
                default. Posters are copied in the background, so they do not
                slow the import itself and may appear shortly after a file is
                indexed. Metadata imports only — setting it on a media import
                raises a 400, since imported media gets real thumbnails from
                the processing pipeline.
            enrich_metadata: Backfill source-metadata fields the connector's
                list endpoint omits, after each index batch settles: Gong
                parties + Call Spotlight content (batched — enriched docs are
                re-embedded so the content is searchable) and Dropbox
                media_info duration/dimensions (per-file). No-op for other
                connectors. Off by default: it spends upstream API budget and,
                for Gong, embedding work. Metadata imports only — setting it
                on a media import raises a 400, since a media run ingests each
                file in full and has no metadata-only record to enrich.

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
                enrich_metadata=enrich_metadata,
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
        """List a collection's bulk imports, newest first, each with its
        latest run inline.

        Args:
            collection_id: The ID of the collection.
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
        """Get a bulk import definition with one page of its run history
        (newest first).

        Args:
            collection_id: The ID of the collection.
            import_id: The ID of the import.
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
        """Delete a bulk import definition and its run history.

        Any active run is cancelled first. Files the import brought into the
        collection are not removed.

        Args:
            collection_id: The ID of the collection.
            import_id: The ID of the import.

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
        enrich_metadata: Optional[bool] = None,
    ):
        """Trigger a new run of a saved import.

        ``mode`` and ``delete_missing`` default to the definition's saved
        values. Only one run may be active per collection at a time;
        triggering while any run in the collection is active raises a
        CloudglueError with status 409. Rerunning is also how a media import
        resumes after it stopped on exhausted credits or a usage limit: an
        'append' run skips files it already imported and retries the rest.

        Args:
            collection_id: The ID of the collection.
            import_id: The ID of the import.
            mode: 'append' or 'refresh'; defaults to the definition's
                default_mode. For media imports, 'refresh' re-syncs the
                source metadata of already-imported files — media bytes are
                never re-downloaded.
            delete_missing: Override the definition's delete-missing behavior
                for this run (refresh runs only).
            max_files: Override the definition's max_files for this run.
            include_thumbnails: Override the definition's include_thumbnails
                for this run (metadata imports only — a 400 otherwise).
            enrich_metadata: Override the definition's enrich_metadata for
                this run (metadata imports only — a 400 otherwise).

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
                enrich_metadata=enrich_metadata,
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
        """Cancel an active bulk import run.

        Files already imported by the run stay in the collection; the run is
        settled and marked cancelled.

        Args:
            collection_id: The ID of the collection.
            import_id: The ID of the import.
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


#: .. deprecated:: 0.7.24
#:    Renamed to :class:`BulkImports` in spec v0.7.21, when bulk imports grew
#:    beyond metadata collections. This alias still works and refers to the
#:    same class.
MetadataImports = BulkImports
