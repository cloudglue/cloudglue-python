# cloudglue/client/resources/query.py
"""Query resource for Cloudglue API."""
import time
from typing import List, Optional

from cloudglue.sdk.models.run_query_request import RunQueryRequest
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Query:
    """Client for the Cloudglue Query API.

    Runs read-only SQL (or natural-language) queries over the structured data
    extracted from collections, against three virtual tables — files,
    entities, and segment_entities — built from each file's most recent
    completed extraction.
    """

    def __init__(self, api):
        """Initialize the Query client.

        Args:
            api: The QueryApi instance.
        """
        self.api = api

    def run(
        self,
        collections: List[str],
        sql: Optional[str] = None,
        query: Optional[str] = None,
        format: Optional[str] = None,
        max_rows: Optional[int] = None,
        background: Optional[bool] = None,
        dry_run: Optional[bool] = None,
    ):
        """Run a read-only SQL query over one or more collections.

        Provide exactly one of `sql` (2 credits) or `query` — a
        natural-language question that Cloudglue compiles to SQL against the
        same virtual schema (4 credits; the compiled statement is returned in
        the result's `sql` field). Results are returned inline and stored, so
        completed runs can be re-fetched via `get()`.

        Args:
            collections: Collection IDs (1-20) whose extracted data to query.
            sql: A single read-only SELECT statement over the virtual tables.
                Exactly one of sql or query must be provided.
            query: A natural-language question to run instead of sql.
            format: Output format ('json', 'csv', 'jsonl') for exports.
            max_rows: Maximum number of rows to return (1-10000).
            background: Run as a background export; poll with `get()` (or
                `wait_for_ready()`) and download via the result's
                download_url.
            dry_run: Validate (and for natural-language queries, compile)
                without executing.

        Returns:
            QueryResult object (inline rows, or export state when background).

        Raises:
            CloudglueError: On invalid/rejected SQL (400), insufficient
                credits (402), unknown collections (404), execution timeout
                (408), oversized datasets (409), uncompilable natural-language
                queries (422), or rate limits (429).
        """
        try:
            request = RunQueryRequest(
                collections=collections,
                sql=sql,
                query=query,
                format=format,
                max_rows=max_rows,
                background=background,
                dry_run=dry_run,
            )
            return self.api.run_query(run_query_request=request)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_schema(self, collections: List[str]):
        """Introspect the virtual tables and per-collection extracted fields.

        Returns column names, entity field names, types, and levels, plus each
        collection's verbatim extract schema and prompt — use before writing a
        query.

        Args:
            collections: Collection IDs (1-20) to introspect.

        Returns:
            QuerySchema object.

        Raises:
            CloudglueError: If there is an error introspecting the schema.
        """
        try:
            return self.api.get_query_schema(collections=",".join(collections))
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
    ):
        """List query runs with pagination and filtering.

        List items omit the columns and rows payloads — fetch an individual
        run via `get()` for the full result.

        Args:
            limit: Maximum number of runs to return (1-100).
            offset: Number of runs to skip.
            status: Filter by status ('completed', 'failed', 'in_progress',
                'cancelled').
            created_before: Filter runs created before a date (YYYY-MM-DD, UTC).
            created_after: Filter runs created after a date (YYYY-MM-DD, UTC).

        Returns:
            QueryListResponse object.

        Raises:
            CloudglueError: If there is an error listing query runs.
        """
        try:
            return self.api.list_queries(
                limit=limit,
                offset=offset,
                status=status,
                created_before=created_before,
                created_after=created_after,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, query_id: str):
        """Retrieve a stored query run by ID, including its result rows.

        Results larger than the inline storage cap are replayed truncated
        (`truncated: true`).

        Args:
            query_id: The ID of the query run.

        Returns:
            QueryResult object.

        Raises:
            CloudglueError: If there is an error retrieving the run.
        """
        try:
            return self.api.get_query(id=query_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def cancel(self, query_id: str):
        """Cancel an in-progress background export.

        The run is marked cancelled synchronously, the export stream is
        aborted mid-flight (the partial upload is discarded), and reserved
        credits are refunded. A run that has already completed or failed is
        returned unchanged.

        Args:
            query_id: The ID of the query run to cancel.

        Returns:
            QueryResult object.

        Raises:
            CloudglueError: If there is an error cancelling the run.
        """
        try:
            return self.api.cancel_query_export(id=query_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def wait_for_ready(
        self,
        query_id: str,
        poll_interval: int = 5,
        timeout: int = 180,
    ):
        """Wait for a background query run to reach a terminal state.

        Polls `get()` until the run is completed, failed, or cancelled.

        Args:
            query_id: The ID of the query run to wait for.
            poll_interval: How often to check the run status (in seconds).
            timeout: Maximum time to wait (in seconds).

        Returns:
            The final QueryResult object.

        Raises:
            CloudglueError: If the run fails or the timeout is reached.
        """
        try:
            elapsed = 0
            while elapsed < timeout:
                run = self.get(query_id)
                if run.status in ("completed", "failed", "cancelled"):
                    if run.status == "failed":
                        raise CloudglueError(f"Query run failed: {query_id}")
                    return run
                time.sleep(poll_interval)
                elapsed += poll_interval
            raise TimeoutError(
                f"Query run did not complete within {timeout} seconds"
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except CloudglueError:
            raise
        except Exception as e:
            raise CloudglueError(str(e))
