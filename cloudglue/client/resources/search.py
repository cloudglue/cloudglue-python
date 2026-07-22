# cloudglue/client/resources/search.py
"""Search resource for Cloudglue API."""
import base64
import os
import pathlib
from typing import List, Dict, Any, Optional, Union, Literal

from cloudglue.sdk.models.search_request import SearchRequest
from cloudglue.sdk.models.search_filter import SearchFilter
from cloudglue.sdk.models.search_filter_criteria import SearchFilterCriteria
from cloudglue.sdk.models.search_filter_metadata_inner import SearchFilterMetadataInner
from cloudglue.sdk.models.search_filter_file_inner import SearchFilterFileInner
from cloudglue.sdk.models.search_filter_video_info_inner import SearchFilterVideoInfoInner
from cloudglue.sdk.models.search_request_source_image import SearchRequestSourceImage
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Search:
    """Client for the Cloudglue Search API."""

    def __init__(self, api):
        """Initialize the Search client.

        Args:
            api: The SearchApi instance.
        """
        self.api = api

    @staticmethod
    def _create_metadata_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
        scope: Optional[Literal['file', 'segment']] = None,
    ) -> SearchFilterMetadataInner:
        """Create a metadata filter for search.
        
        Args:
            path: JSON path on metadata object (e.g. 'my_custom_field', 'category.subcategory')
            operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
            value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
            value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            scope: Specifies scope of eligible search items to check metadata filtering conditions.
                   'file' checks file-level metadata, 'segment' checks segment-level metadata.
                   Defaults to 'file' if not specified.
            
        Returns:
            SearchFilterMetadataInner object
        """
        return SearchFilterMetadataInner(
            path=path,
            operator=operator,
            value_text=value_text,
            value_text_array=value_text_array,
            scope=scope,
        )

    @staticmethod
    def _create_video_info_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
        scope: Optional[Literal['file', 'segment']] = None,
    ) -> SearchFilterVideoInfoInner:
        """Create a video info filter for search.

        Args:
            path: Video info field ('duration_seconds', 'has_audio')
            operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
            value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
            value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            scope: Scope of the filter. 'file' filters by source video properties,
                   'segment' filters by segment properties. Only duration_seconds is
                   supported with segment scope. Defaults to 'file'.

        Returns:
            SearchFilterVideoInfoInner object
        """
        return SearchFilterVideoInfoInner(
            path=path,
            operator=operator,
            value_text=value_text,
            value_text_array=value_text_array,
            scope=scope,
        )

    @staticmethod
    def _create_file_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
    ) -> SearchFilterFileInner:
        """Create a file filter for search.
        
        Args:
            path: File field ('bytes', 'filename', 'uri', 'created_at', 'id')
            operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
            value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
            value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            
        Returns:
            SearchFilterFileInner object
        """
        return SearchFilterFileInner(
            path=path,
            operator=operator,
            value_text=value_text,
            value_text_array=value_text_array,
        )

    @staticmethod
    def create_filter(
        metadata_filters: Optional[List[Dict[str, Any]]] = None,
        video_info_filters: Optional[List[Dict[str, Any]]] = None,
        file_filters: Optional[List[Dict[str, Any]]] = None,
        source_metadata_filters: Optional[List[Dict[str, Any]]] = None,
    ) -> SearchFilter:
        """Create a search filter using simple dictionaries.
        
        This is the main method for creating search filters. It allows you to create filters 
        using simple dictionaries instead of working with the underlying filter objects.
        
        Args:
            metadata_filters: List of metadata filter dictionaries. Each dict should have:
                - 'path': JSON path on metadata object
                - 'operator': Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
                - 'value_text': (optional) Text value for scalar comparison  
                - 'value_text_array': (optional) Array of values for array comparisons
                - 'scope': (optional) Scope of eligible search items ('file' or 'segment'). Defaults to 'file'.
            video_info_filters: List of video info filter dictionaries. Same structure as metadata_filters,
                plus optional 'scope' ('file' or 'segment'). Defaults to 'file'.
            file_filters: List of file filter dictionaries (same structure, without scope)
            source_metadata_filters: List of connector source-metadata filter dictionaries
                (same structure, without scope — file scope only). Paths address the
                connector-provided `source_metadata` object, e.g. 'topic' (zoom),
                'title' (gong/grain/iconik), 'participants.name' (grain),
                'parties.email' (gong), 'name' (google-drive/dropbox),
                'media_type' (iconik), or 'iconik_metadata.<FieldName>' (iconik
                custom metadata-view fields, use ContainsAny for list fields).
                Paths through arrays of objects match when ANY element matches.

        Returns:
            SearchFilter object
            
        Example:
            filter = client.search.create_filter(
                metadata_filters=[
                    {'path': 'category', 'operator': 'Equal', 'value_text': 'tutorial'},
                    {'path': 'tags', 'operator': 'ContainsAny', 'value_text_array': ['python', 'programming']},
                    {'path': 'segment_type', 'operator': 'Equal', 'value_text': 'intro', 'scope': 'segment'}
                ],
                video_info_filters=[
                    {'path': 'duration_seconds', 'operator': 'LessThan', 'value_text': '600'}
                ]
            )
        """
        metadata_objs = None
        if metadata_filters:
            metadata_objs = [
                SearchFilterMetadataInner(**f) for f in metadata_filters
            ]
            
        video_info_objs = None
        if video_info_filters:
            video_info_objs = [
                SearchFilterVideoInfoInner(**f) for f in video_info_filters
            ]
            
        file_objs = None
        if file_filters:
            file_objs = [
                SearchFilterFileInner(**f) for f in file_filters
            ]

        source_metadata_objs = None
        if source_metadata_filters:
            source_metadata_objs = [
                SearchFilterCriteria(**f) for f in source_metadata_filters
            ]

        return SearchFilter(
            metadata=metadata_objs,
            video_info=video_info_objs,
            file=file_objs,
            source_metadata=source_metadata_objs,
        )

    def search(
        self,
        scope: str,
        collections: List[str],
        query: Optional[str] = None,
        limit: Optional[int] = None,
        filter: Optional[Union[SearchFilter, Dict[str, Any]]] = None,
        source_image: Optional[Union[str, Dict[str, Any]]] = None,
        group_by_key: Optional[str] = None,
        threshold: Optional[Union[int, float]] = None,
        sort_by: Optional[str] = None,
        search_modalities: Optional[List[str]] = None,
        label_filters: Optional[List[str]] = None,
        **kwargs,
    ):
        """Search across video files and segments to find relevant content.

        Args:
            scope: Search scope - 'file' searches at file level (requires collections with enable_summary=true), 
                   'segment' searches at segment level, 'face' searches for faces in videos using image matching
            collections: List of collection IDs to search within. 
                        For text search (scope='file' or 'segment'): Must be rich-transcript collections 
                        (collection_type='rich-transcripts' or 'media-descriptions'). For file-level search, 
                        collections must have 'enable_summary: true' in transcribe_config.
                        For face search (scope='face'): Must be face-analysis collections (collection_type='face-analysis').
            query: Text search query to find relevant content (required for scope='file' or 'segment', not used for scope='face')
            limit: Maximum number of search results to return (1-100, default 10). When group_by_key is specified,
                   this applies to total items across groups (not the number of groups).
            filter: Filter criteria to constrain search results. Can be a SearchFilter object
                   or a dictionary with 'metadata', 'video_info', and/or 'file' keys.
            source_image: Source image for face search (required for scope='face'). Can be:
                - URL string (public image URL)
                - Local file path (will be converted to base64)
                - Base64 string (raw base64 or with data: prefix)
                - Dictionary with 'url' or 'base64' keys
            group_by_key: Optional key to group results by. Currently only 'file' is supported.
                         Cannot be used with scope='file'. When specified, results are grouped by file_id.
            threshold: Optional minimum score threshold to filter results. Can be any real number.
            sort_by: Optional sort order for results. Default: 'score'. When group_by_key is specified,
                    can also use 'item_count' to sort by number of items per group.
            search_modalities: Optional list of search modalities to use. Valid values are:
                - 'general_content': General content search based on visual/spoken content similarity
                - 'speech_lexical': Keyword and exact match search against speech content
                - 'ocr_lexical': Keyword and exact match search against screen text (OCR) content
                - 'tag_semantic': Semantic similarity search against tag values
                - 'tag_lexical': Keyword and exact match search against tag values
                If not specified, general_content will be used. Currently only one modality per request.
            label_filters: Optional list of label strings to filter eligible search items by presence of 
                          one or more labels. Only supported for 'tag_semantic' and 'tag_lexical' search 
                          modalities. If not specified, all tags will be considered.
            **kwargs: Additional parameters for the request.

        Returns:
            SearchResponse: The API response with search results.

        Raises:
            CloudglueError: If there is an error making the API request or processing the response.

        Example:
            # Text search for content in collections
            results = client.search.search(
                scope="segment",
                collections=["collection_123"],
                query="machine learning tutorial",
                limit=20
            )
            
            # Text search with filters
            search_filter = client.search.create_filter(
                metadata_filters=[
                    {'path': 'category', 'operator': 'Equal', 'value_text': 'tutorial'}
                ]
            )
            results = client.search.search(
                scope="file",
                collections=["collection_123"],
                query="python programming",
                filter=search_filter
            )
            
            # Face search
            results = client.search.search(
                scope="face",
                collections=["face_collection_123"],
                source_image="https://example.com/image.jpg",
                limit=20
            )
            
            # Tag-based search with label filters
            results = client.search.search(
                scope="segment",
                collections=["collection_123"],
                query="person",
                search_modalities=["tag_semantic"],
                label_filters=["speaker", "character"]
            )
        """
        try:
            # Handle filter parameter
            if filter is not None:
                if isinstance(filter, dict):
                    # Convert dictionary to SearchFilter
                    filter = SearchFilter.from_dict(filter)
                elif isinstance(filter, SearchFilter):
                    # Already the correct type, no conversion needed
                    pass
                else:
                    raise ValueError("filter must be a SearchFilter object or dictionary")
            
            # Handle source_image parameter for face search
            source_image_obj = None
            if source_image is not None:
                if isinstance(source_image, dict):
                    # Already in SearchRequestSourceImage format
                    source_image_obj = SearchRequestSourceImage(**source_image)
                elif isinstance(source_image, str):
                    if source_image.startswith(('http://', 'https://')):
                        # URL
                        source_image_obj = SearchRequestSourceImage(url=source_image)
                    elif source_image.startswith('data:image/'):
                        # Data URL - extract base64 part
                        base64_part = source_image.split(',')[1] if ',' in source_image else source_image
                        source_image_obj = SearchRequestSourceImage(base64=base64_part)
                    elif os.path.exists(source_image):
                        # File path - encode to base64
                        # Check file extension
                        file_ext = pathlib.Path(source_image).suffix.lower()
                        if file_ext not in ['.jpg', '.jpeg', '.png']:
                            raise CloudglueError(f"Unsupported file type: {file_ext}. Only JPG and PNG are supported.")
                        
                        # Read and encode the file
                        with open(source_image, 'rb') as image_file:
                            image_data = image_file.read()
                            base64_string = base64.b64encode(image_data).decode('utf-8')
                            source_image_obj = SearchRequestSourceImage(base64=base64_string)
                    else:
                        # Assume raw base64 string
                        source_image_obj = SearchRequestSourceImage(base64=source_image)
                else:
                    raise CloudglueError("source_image must be a string (URL, file path, or base64) or dictionary")
            
            request = SearchRequest(
                scope=scope,
                collections=collections,
                query=query,
                limit=limit,
                filter=filter,
                source_image=source_image_obj,
                group_by_key=group_by_key,
                threshold=threshold,
                sort_by=sort_by,
                search_modalities=search_modalities,
                label_filters=label_filters,
                **kwargs,
            )
            return self.api.search_content(search_request=request)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            if isinstance(e, CloudglueError):
                raise
            raise CloudglueError(str(e))

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List search responses.

        Get a list of search responses, ordered by created_at in descending order.

        Args:
            limit: Maximum number of search responses to return (1-100)
            offset: Number of search responses to skip

        Returns:
            SearchResponseList object

        Raises:
            CloudglueError: If there is an error listing search responses.
        """
        try:
            response = self.api.get_search(
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, search_id: str):
        """Get a search response by ID.

        Args:
            search_id: The ID of the search response to retrieve

        Returns:
            SearchResponse object

        Raises:
            CloudglueError: If there is an error retrieving the search response.
        """
        try:
            response = self.api.get_search_by_id(search_id=search_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

