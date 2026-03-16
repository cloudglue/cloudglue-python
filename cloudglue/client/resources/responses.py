# cloudglue/client/resources/responses.py
"""Responses resource for Cloudglue API."""
import json
from typing import List, Dict, Any, Optional, Union, Generator

from cloudglue.sdk.models.create_response_request import CreateResponseRequest
from cloudglue.sdk.models.create_response_request_input import CreateResponseRequestInput
from cloudglue.sdk.models.entity_backed_knowledge_config import EntityBackedKnowledgeConfig
from cloudglue.sdk.models.entity_collection_config import EntityCollectionConfig
from cloudglue.sdk.models.knowledge_base_collections import KnowledgeBaseCollections
from cloudglue.sdk.models.knowledge_base_default import KnowledgeBaseDefault
from cloudglue.sdk.models.knowledge_base_files import KnowledgeBaseFiles
from cloudglue.sdk.models.response_input_content import ResponseInputContent
from cloudglue.sdk.models.response_input_message import ResponseInputMessage
from cloudglue.sdk.models.response_knowledge_base import ResponseKnowledgeBase
from cloudglue.sdk.models.search_filter import SearchFilter
from cloudglue.sdk.models.search_filter_file_inner import SearchFilterFileInner
from cloudglue.sdk.models.search_filter_metadata_inner import SearchFilterMetadataInner
from cloudglue.sdk.models.search_filter_video_info_inner import SearchFilterVideoInfoInner
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


def _normalize_input(input: Union[str, List[Dict[str, Any]]]) -> CreateResponseRequestInput:
    """Normalize user-friendly input into a CreateResponseRequestInput.

    Accepts:
        - A plain string: "What does amy talk about"
        - A list of simple message dicts: [{"role": "user", "content": "Hello"}]
        - A list of fully-structured message dicts matching the API schema
    """
    if isinstance(input, str):
        return CreateResponseRequestInput(input)

    # Normalize list of message dicts into ResponseInputMessage objects
    messages = []
    for msg in input:
        # If content is a plain string, wrap it in the expected structure
        content = msg.get("content")
        if isinstance(content, str):
            content = [ResponseInputContent(type="input_text", text=content)]
        elif isinstance(content, list):
            content = [
                ResponseInputContent(type=c.get("type", "input_text"), text=c["text"])
                if isinstance(c, dict) else c
                for c in content
            ]
        messages.append(ResponseInputMessage(
            type=msg.get("type", "message"),
            role=msg["role"],
            content=content,
        ))
    return CreateResponseRequestInput(messages)


def _iter_sse_events(raw_response) -> Generator[Dict[str, Any], None, None]:
    """Parse SSE events from a raw urllib3.HTTPResponse.

    Yields dicts with shape {'event': str|None, 'data': dict|str}.
    The data field is JSON-parsed when possible; the [DONE] sentinel is yielded as-is.
    """
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
                # Empty line signals end of an SSE event
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

    # Handle any remaining data in buffer after stream ends
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


class Responses:
    """Handles response operations for the Cloudglue API."""

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        input: Union[str, List[Dict[str, Any]]],
        collections: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        use_default_index: bool = False,
        model: str = "nimbus-001",
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        background: Optional[bool] = None,
        include: Optional[List[str]] = None,
        stream: Optional[bool] = None,
        knowledge_base_type: Optional[str] = None,
        entity_backed_knowledge_config: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """Create a new response.

        Exactly one of `collections`, `files`, or `use_default_index=True` must be provided
        to specify the knowledge base source.

        Args:
            input: The input for the response. Can be a simple string (treated as user message)
                or a list of message dicts with 'role' and 'content' keys.
            collections: List of collection IDs to search for relevant context.
            files: List of file references to search (file UUIDs, cloudglue URIs, or URLs).
            use_default_index: When True, search all default-indexed files for the account.
            model: The model to use for the response (default: 'nimbus-001').
            instructions: Optional system instructions to guide the model's behavior.
            temperature: Sampling temperature for the model (0-2, default: 0.7).
            background: Set to True to process the response in the background.
            include: Additional data to include in the response annotations.
            stream: Set to True to stream the response via SSE. Mutually exclusive with background.
            knowledge_base_type: The type of knowledge base interaction pattern.
                'general_question_answering' (default) or 'entity_backed_knowledge'.
                Only applies when using collections knowledge base.
            entity_backed_knowledge_config: Configuration for entity-backed knowledge.
                Required when knowledge_base_type is 'entity_backed_knowledge'.
                Only applies when using collections knowledge base.
            filter: Optional filter to narrow down the search within collections.
                Only applies when using collections knowledge base.
            tools: Optional list of tool definitions for function calling.

        Returns:
            The Response object, or a generator of SSE event dicts when stream=True.

        Raises:
            CloudglueError: If there is an error creating the response.
        """
        try:
            sources = sum([bool(collections), bool(files), use_default_index])
            if sources != 1:
                raise ValueError(
                    "Exactly one of 'collections', 'files', or 'use_default_index=True' must be provided"
                )

            if collections:
                kb_kwargs = {"collections": collections}
                if knowledge_base_type is not None:
                    kb_kwargs["type"] = knowledge_base_type
                if filter is not None:
                    kb_kwargs["filter"] = SearchFilter.from_dict(filter) if isinstance(filter, dict) else filter
                if entity_backed_knowledge_config is not None:
                    kb_kwargs["entity_backed_knowledge_config"] = (
                        EntityBackedKnowledgeConfig.from_dict(entity_backed_knowledge_config)
                        if isinstance(entity_backed_knowledge_config, dict)
                        else entity_backed_knowledge_config
                    )
                kb_inner = KnowledgeBaseCollections(**kb_kwargs)
            elif files:
                kb_inner = KnowledgeBaseFiles(source="files", files=files)
            else:
                kb_inner = KnowledgeBaseDefault(source="default")

            knowledge_base = ResponseKnowledgeBase(kb_inner)

            request = CreateResponseRequest(
                input=_normalize_input(input),
                model=model,
                knowledge_base=knowledge_base,
                instructions=instructions,
                temperature=temperature,
                background=background,
                include=include,
                stream=stream,
                tools=tools,
            )

            if stream:
                raw_response = self.api.create_response_without_preload_content(
                    create_response_request=request
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
                return self.api.create_response(create_response_request=request)
        except CloudglueError:
            raise
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, response_id: str):
        """Get a specific response by ID.

        Args:
            response_id: The ID of the response to retrieve.

        Returns:
            The Response object.

        Raises:
            CloudglueError: If there is an error retrieving the response.
        """
        try:
            return self.api.get_response(id=response_id)
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
        """List responses with optional filtering.

        Args:
            limit: Maximum number of responses to return.
            offset: Number of responses to skip.
            status: Filter by status.
            created_before: Filter by creation date (YYYY-MM-DD format, UTC).
            created_after: Filter by creation date (YYYY-MM-DD format, UTC).

        Returns:
            ResponseList object containing responses.

        Raises:
            CloudglueError: If there is an error listing responses.
        """
        try:
            return self.api.list_responses(
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

    def delete(self, response_id: str):
        """Delete a response.

        Args:
            response_id: The ID of the response to delete.

        Returns:
            Deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the response.
        """
        try:
            return self.api.delete_response(id=response_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def cancel(self, response_id: str):
        """Cancel a background response that is in progress.

        Args:
            response_id: The ID of the response to cancel.

        Returns:
            The Response object (may be completed, failed, or cancelled).

        Raises:
            CloudglueError: If there is an error cancelling the response.
        """
        try:
            return self.api.cancel_response(id=response_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    @staticmethod
    def create_entity_collection_config(
        collection_id: str,
        name: str,
        description: str,
    ) -> EntityCollectionConfig:
        """Create an entity collection configuration for use with entity-backed knowledge.

        Args:
            collection_id: UUID of the entity collection.
            name: Name for the entity collection (e.g., 'action_items', 'speakers_and_roles').
                Used by the model to decide which collection to query.
            description: Human-readable description of what this entity collection contains.
                Helps the model decide when to use this collection.

        Returns:
            EntityCollectionConfig object

        Example:
            config = client.responses.create_entity_collection_config(
                collection_id="ad208730-9044-4b17-ab28-ffd91b074dee",
                name="action_items",
                description="Action items extracted from meeting recordings",
            )
        """
        return EntityCollectionConfig(
            collection_id=collection_id,
            name=name,
            description=description,
        )

    @staticmethod
    def create_entity_backed_knowledge_config(
        entity_collections: List[Union[EntityCollectionConfig, Dict[str, Any]]],
        description: Optional[str] = None,
    ) -> EntityBackedKnowledgeConfig:
        """Create an entity-backed knowledge configuration.

        Required when using knowledge_base_type='entity_backed_knowledge' with nimbus-002-preview.

        Args:
            entity_collections: List of entity collection configs. Each can be an
                EntityCollectionConfig object or a dict with 'collection_id', 'name',
                and 'description' keys.
            description: Optional context about the videos in this collection. Helps the model
                understand the domain (max 2000 chars).

        Returns:
            EntityBackedKnowledgeConfig object

        Example:
            entity_config = client.responses.create_entity_backed_knowledge_config(
                entity_collections=[
                    client.responses.create_entity_collection_config(
                        collection_id="ad208730-...",
                        name="action_items",
                        description="Action items from meetings",
                    )
                ],
                description="Sales call recordings from Q4 2024",
            )
        """
        normalized = []
        for ec in entity_collections:
            if isinstance(ec, dict):
                normalized.append(EntityCollectionConfig.from_dict(ec))
            else:
                normalized.append(ec)
        return EntityBackedKnowledgeConfig(
            entity_collections=normalized,
            description=description,
        )

    @staticmethod
    def create_filter(
        metadata: Optional[List[Dict[str, Any]]] = None,
        video_info: Optional[List[Dict[str, Any]]] = None,
        file: Optional[List[Dict[str, Any]]] = None,
    ) -> SearchFilter:
        """Create a search filter to narrow down results within collections.

        Each filter criterion is a dict with 'path', 'operator', and 'valueText' or 'valueTextArray'.

        Supported operators: Equal, NotEqual, LessThan, GreaterThan, In, ContainsAny, ContainsAll, Like.

        Args:
            metadata: Filter by file metadata using JSON path expressions.
                Each item: {'path': str, 'operator': str, 'valueText': str} or
                {'path': str, 'operator': str, 'valueTextArray': [str, ...]}.
                Optional 'scope' key ('file' or 'segment', default 'file').
            video_info: Filter by video information (e.g., duration_seconds).
            file: Filter by file properties. Valid paths: 'bytes', 'filename', 'uri',
                'created_at', 'id'.

        Returns:
            SearchFilter object

        Example:
            # Filter to a specific file
            f = client.responses.create_filter(
                file=[{"path": "id", "operator": "Equal", "valueText": "file-uuid"}]
            )

            # Filter by metadata
            f = client.responses.create_filter(
                metadata=[{"path": "speaker", "operator": "Equal", "valueText": "Amy"}]
            )

            # Filter by video duration > 60s
            f = client.responses.create_filter(
                video_info=[{"path": "duration_seconds", "operator": "GreaterThan", "valueText": "60"}]
            )
        """
        return SearchFilter(
            metadata=[SearchFilterMetadataInner.from_dict(m) for m in metadata] if metadata else None,
            video_info=[SearchFilterVideoInfoInner.from_dict(v) for v in video_info] if video_info else None,
            file=[SearchFilterFileInner.from_dict(f) for f in file] if file else None,
        )
