# cloudglue/client/resources/deep_search.py
"""Deep Search resource for Cloudglue API."""
import json
from typing import List, Dict, Any, Optional, Union, Generator

from cloudglue.sdk.models.create_deep_search_request import CreateDeepSearchRequest
from cloudglue.sdk.models.create_deep_search_request_knowledge_base import CreateDeepSearchRequestKnowledgeBase
from cloudglue.sdk.models.deep_search_kb_collections import DeepSearchKBCollections
from cloudglue.sdk.models.deep_search_kb_files import DeepSearchKBFiles
from cloudglue.sdk.models.deep_search_kb_default import DeepSearchKBDefault
from cloudglue.sdk.models.search_filter import SearchFilter
from cloudglue.sdk.models.search_filter_file_inner import SearchFilterFileInner
from cloudglue.sdk.models.search_filter_metadata_inner import SearchFilterMetadataInner
from cloudglue.sdk.models.search_filter_video_info_inner import SearchFilterVideoInfoInner
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


def _iter_sse_events(raw_response) -> Generator[Dict[str, Any], None, None]:
    """Parse SSE events from a raw urllib3.HTTPResponse."""
    buffer = ""
    current_event = None
    current_data_lines = []

    for chunk in raw_response.stream(amt=4096, decode_content=True):
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8")
        buffer += chunk

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.rstrip("\r")

            if line.startswith("event:"):
                current_event = line[len("event:"):].strip()
            elif line.startswith("data:"):
                current_data_lines.append(line[len("data:"):].strip())
            elif line == "":
                if current_data_lines:
                    raw_data = "\n".join(current_data_lines)
                    if raw_data == "[DONE]":
                        parsed_data = raw_data
                    else:
                        try:
                            parsed_data = json.loads(raw_data)
                        except json.JSONDecodeError:
                            parsed_data = raw_data
                    yield {"event": current_event, "data": parsed_data}
                current_event = None
                current_data_lines = []

    if current_data_lines:
        raw_data = "\n".join(current_data_lines)
        if raw_data == "[DONE]":
            parsed_data = raw_data
        else:
            try:
                parsed_data = json.loads(raw_data)
            except json.JSONDecodeError:
                parsed_data = raw_data
        yield {"event": current_event, "data": parsed_data}


class DeepSearch:
    """Client for the Cloudglue Deep Search API.

    Deep search uses agentic retrieval and LLM summarization to find
    specific moments across your video data.
    """

    def __init__(self, api):
        """Initialize the DeepSearch client.

        Args:
            api: The DeepSearchApi instance.
        """
        self.api = api

    def create(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        use_default_index: bool = False,
        scope: Optional[str] = None,
        limit: Optional[int] = None,
        exclude_weak_results: Optional[bool] = None,
        include: Optional[List[str]] = None,
        stream: Optional[bool] = None,
        background: Optional[bool] = None,
        filter: Optional[Union[SearchFilter, Dict[str, Any]]] = None,
    ):
        """Create a new deep search.

        Exactly one of `collections`, `files`, or `use_default_index=True` must be provided
        to specify the knowledge base source.

        Args:
            query: The search query.
            collections: List of collection IDs to search within.
            files: List of file references to search (file UUIDs, cloudglue URIs, or URLs).
            use_default_index: When True, search all default-indexed files for the account.
            scope: Scope of results - 'segment' (default) or 'file'.
            limit: Maximum number of results (1-500, default 20).
            exclude_weak_results: When True, removes weak matches from results.
            include: Additional fields to include (e.g., ['search_queries']).
            stream: Stream the response via SSE. Mutually exclusive with background.
            background: Process in the background. Mutually exclusive with stream.
            filter: Filter to narrow search within collections. Only applies when using
                collections knowledge base. Can be a SearchFilter object or dict.

        Returns:
            DeepSearch object, or a generator of SSE event dicts when stream=True.

        Raises:
            CloudglueError: If there is an error creating the deep search.
        """
        try:
            # Build knowledge base
            sources = sum([bool(collections), bool(files), use_default_index])
            if sources != 1:
                raise ValueError(
                    "Exactly one of 'collections', 'files', or 'use_default_index=True' must be provided"
                )

            if collections:
                filter_obj = None
                if filter is not None:
                    if isinstance(filter, dict):
                        filter_obj = SearchFilter.from_dict(filter)
                    else:
                        filter_obj = filter
                kb_inner = DeepSearchKBCollections(
                    source="collections",
                    collections=collections,
                    filter=filter_obj,
                )
            elif files:
                kb_inner = DeepSearchKBFiles(source="files", files=files)
            else:
                kb_inner = DeepSearchKBDefault(source="default")

            knowledge_base = CreateDeepSearchRequestKnowledgeBase(kb_inner)

            request = CreateDeepSearchRequest(
                knowledge_base=knowledge_base,
                query=query,
                scope=scope,
                limit=limit,
                exclude_weak_results=exclude_weak_results,
                include=include,
                stream=stream,
                background=background,
            )

            if stream:
                raw_response = self.api.create_deep_search_without_preload_content(
                    create_deep_search_request=request,
                )
                if raw_response.status != 200:
                    error_body = raw_response.read().decode("utf-8")
                    raise CloudglueError(
                        f"({raw_response.status})\nReason: {raw_response.reason}\n"
                        f"HTTP response body: {error_body}",
                        raw_response.status,
                    )
                return _iter_sse_events(raw_response)
            else:
                return self.api.create_deep_search(
                    create_deep_search_request=request,
                )
        except CloudglueError:
            raise
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, deep_search_id: str):
        """Get a deep search by ID.

        Args:
            deep_search_id: The ID of the deep search to retrieve.

        Returns:
            DeepSearch object.

        Raises:
            CloudglueError: If there is an error retrieving the deep search.
        """
        try:
            return self.api.get_deep_search(id=deep_search_id)
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
        """List deep searches with optional filtering.

        Args:
            limit: Maximum number of deep searches to return (1-100).
            offset: Number of deep searches to skip.
            status: Filter by status ('in_progress', 'completed', 'failed', 'cancelled').
            created_before: Filter by creation date (YYYY-MM-DD format, UTC).
            created_after: Filter by creation date (YYYY-MM-DD format, UTC).

        Returns:
            DeepSearchList object.

        Raises:
            CloudglueError: If there is an error listing deep searches.
        """
        try:
            return self.api.list_deep_searches(
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

    def cancel(self, deep_search_id: str):
        """Cancel a background deep search that is in progress.

        Args:
            deep_search_id: The ID of the deep search to cancel.

        Returns:
            DeepSearch object (may be completed, failed, or cancelled).

        Raises:
            CloudglueError: If there is an error cancelling the deep search.
        """
        try:
            return self.api.cancel_deep_search(id=deep_search_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, deep_search_id: str):
        """Delete a deep search.

        Args:
            deep_search_id: The ID of the deep search to delete.

        Returns:
            Deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the deep search.
        """
        try:
            return self.api.delete_deep_search(id=deep_search_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    @staticmethod
    def create_filter(
        metadata: Optional[List[Dict[str, Any]]] = None,
        video_info: Optional[List[Dict[str, Any]]] = None,
        file: Optional[List[Dict[str, Any]]] = None,
    ) -> SearchFilter:
        """Create a search filter for deep search.

        Args:
            metadata: Filter by file metadata. Each item: {'path': str, 'operator': str, 'valueText': str}.
            video_info: Filter by video information (e.g., duration_seconds).
            file: Filter by file properties ('bytes', 'filename', 'uri', 'created_at', 'id').

        Returns:
            SearchFilter object.
        """
        return SearchFilter(
            metadata=[SearchFilterMetadataInner.from_dict(m) for m in metadata] if metadata else None,
            video_info=[SearchFilterVideoInfoInner.from_dict(v) for v in video_info] if video_info else None,
            file=[SearchFilterFileInner.from_dict(f) for f in file] if file else None,
        )
