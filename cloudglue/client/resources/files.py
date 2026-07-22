# cloudglue/client/resources/files.py
"""Files resource for Cloudglue API."""
import json
import os
import pathlib
import time
from typing import List, Dict, Any, Optional, Union

from cloudglue.sdk.models.file_update import FileUpdate
from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.search_filter import SearchFilter
from cloudglue.sdk.models.search_filter_criteria import SearchFilterCriteria
from cloudglue.sdk.models.search_filter_file_inner import SearchFilterFileInner
from cloudglue.sdk.models.search_filter_video_info_inner import SearchFilterVideoInfoInner
from cloudglue.sdk.models.thumbnails_config import ThumbnailsConfig
from cloudglue.sdk.api.segmentations_api import SegmentationsApi
from cloudglue.sdk.models.create_file_segmentation_request import CreateFileSegmentationRequest
from cloudglue.sdk.models.frame_extraction_uniform_config import FrameExtractionUniformConfig
from cloudglue.sdk.models.frame_extraction_thumbnails_config import FrameExtractionThumbnailsConfig
from cloudglue.sdk.models.create_file_frame_extraction_request import CreateFileFrameExtractionRequest
from cloudglue.sdk.models.sync_file_from_url_request import SyncFileFromUrlRequest
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Files:
    """Handles file operations."""

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    @staticmethod
    def _create_metadata_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
    ) -> SearchFilterCriteria:
        """Create a metadata filter for file listing.
        
        Args:
            path: JSON path on metadata object (e.g. 'my_custom_field', 'category.subcategory')
            operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
            value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
            value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            
        Returns:
            SearchFilterCriteria object
        """
        return SearchFilterCriteria(
            path=path,
            operator=operator,
            value_text=value_text,
            value_text_array=value_text_array,
        )

    @staticmethod
    def _create_video_info_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
    ) -> SearchFilterVideoInfoInner:
        """Create a video info filter for file listing.
        
        Args:
            path: JSON path on video_info object ('duration_seconds', 'has_audio')
            operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
            value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
            value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            
        Returns:
            SearchFilterVideoInfoInner object
        """
        return SearchFilterVideoInfoInner(
            path=path,
            operator=operator,
            value_text=value_text,
            value_text_array=value_text_array,
        )

    @staticmethod
    def _create_file_filter(
        path: str,
        operator: str,
        value_text: Optional[str] = None,
        value_text_array: Optional[List[str]] = None,
    ) -> SearchFilterFileInner:
        """Create a file property filter for file listing.
        
        Args:
            path: JSON path on file object ('bytes', 'filename', 'uri', 'created_at', 'id')
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
    ) -> SearchFilter:
        """Create a filter object for file listing.

        Args:
            metadata_filters: List of metadata filter dictionaries. Each dict should contain:
                - path: JSON path on metadata object (e.g. 'my_custom_field', 'category.subcategory')
                - operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
                - value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
                - value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            video_info_filters: List of video info filter dictionaries. Each dict should contain:
                - path: JSON path on video_info object ('duration_seconds', 'has_audio')
                - operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
                - value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
                - value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)
            file_filters: List of file property filter dictionaries. Each dict should contain:
                - path: JSON path on file object ('bytes', 'filename', 'uri', 'created_at', 'id')
                - operator: Comparison operator ('NotEqual', 'Equal', 'LessThan', 'GreaterThan', 'In', 'ContainsAny', 'ContainsAll', 'Like')
                - value_text: Text value for scalar comparison (used with NotEqual, Equal, LessThan, GreaterThan, Like)
                - value_text_array: Array of values for array comparisons (used with ContainsAny, ContainsAll, In)

        Returns:
            SearchFilter object

        Examples:
            # Filter by metadata
            filter_obj = Files.create_filter(
                metadata_filters=[
                    {"path": "speaker", "operator": "Equal", "value_text": "John"}
                ]
            )

            # Filter by video info
            filter_obj = Files.create_filter(
                video_info_filters=[
                    {"path": "duration_seconds", "operator": "GreaterThan", "value_text": "60"}
                ]
            )

            # Filter by file properties
            filter_obj = Files.create_filter(
                file_filters=[
                    {"path": "filename", "operator": "Like", "value_text": "%.mp4"}
                ]
            )

            # Combined filtering
            filter_obj = Files.create_filter(
                metadata_filters=[
                    {"path": "speaker", "operator": "Equal", "value_text": "John"}
                ],
                video_info_filters=[
                    {"path": "has_audio", "operator": "Equal", "value_text": "true"}
                ],
                file_filters=[
                    {"path": "filename", "operator": "Like", "value_text": "%.mp4"}
                ]
            )
        """
        metadata = None
        if metadata_filters:
            metadata = [
                Files._create_metadata_filter(**filter_dict) for filter_dict in metadata_filters
            ]

        video_info = None
        if video_info_filters:
            video_info = [
                Files._create_video_info_filter(**filter_dict) for filter_dict in video_info_filters
            ]

        file = None
        if file_filters:
            file = [
                Files._create_file_filter(**filter_dict) for filter_dict in file_filters
            ]

        return SearchFilter(
            metadata=metadata,
            video_info=video_info,
            file=file,
        )

    def upload(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        enable_segment_thumbnails: Optional[bool] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Upload a file to Cloudglue.

        Accepts video, audio, or image files. Image files are processed at the
        file level only (no segmentation), so segmentation/thumbnail options do
        not apply to them.

        Args:
            file_path: Path to the local file to upload (video, audio, or image).
            metadata: Optional user-provided metadata about the file.
            enable_segment_thumbnails: Whether to generate thumbnails for each segment.
            wait_until_finish: Whether to wait for the file processing to complete.
            poll_interval: How often to check the file status (in seconds) if waiting.
            timeout: Maximum time to wait for processing (in seconds) if waiting.

        Returns:
            The uploaded file object. If wait_until_finish is True, waits for processing
            to complete and returns the final file state.

        Raises:
            CloudglueError: If there is an error uploading or processing the file.
        """
        try:
            file_path = pathlib.Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file as bytes and create a tuple of (filename, bytes)
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            filename = os.path.basename(file_path)
            file_tuple = (filename, file_bytes)

            response = self.api.upload_file(
                file=file_tuple, 
                metadata=metadata,
                enable_segment_thumbnails=enable_segment_thumbnails
            )

            # If not waiting for completion, return immediately
            if not wait_until_finish:
                return response

            # Otherwise poll until completion or timeout
            file_id = response.id
            elapsed = 0
            terminal_states = ["ready", "completed", "failed", "not_applicable"]

            while elapsed < timeout:
                status = self.get(file_id=file_id)

                if status.status in terminal_states:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"File processing did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def sync_from_url(
        self,
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        enable_segment_thumbnails: Optional[bool] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Materialize a publicly accessible URL into a Cloudglue file.

        Syncs the media at the given URL without requiring a data connector or
        a collection. Idempotent: syncing the same URL returns the existing
        file.

        Accepted URL forms:
            - Direct http(s) video/audio/image file URLs (e.g. `.mp4`, `.jpg`, `.png`, `.webp`)
            - Public Dropbox share links (`dropbox.com/scl/fi/...`, `/s/...`)
            - TikTok video URLs (consumes scrape credits)
            - Loom share URLs (`https://www.loom.com/share/<id>`)

        Not supported here: YouTube URLs (collection-only — use
        `collections.add_media`) and connector-native URLs (`s3://`, `gs://`,
        `gdrive://`, Zoom/Grain links, ... — use `data_connectors.sync_file`).

        Args:
            url: Publicly accessible URL to sync.
            metadata: Optional user-provided metadata about the file. Ignored
                if the URL was already synced (the existing file is returned
                unchanged).
            enable_segment_thumbnails: Whether to generate per-segment
                thumbnails for the file. Defaults to True server-side,
                matching file upload.
            wait_until_finish: Whether to wait for the file processing to complete.
            poll_interval: How often to check the file status (in seconds) if waiting.
            timeout: Maximum time to wait for processing (in seconds) if waiting.

        Returns:
            The synced file object. If wait_until_finish is True, waits for
            processing to complete and returns the final file state.

        Raises:
            CloudglueError: If there is an error syncing or processing the file.
        """
        try:
            request_kwargs: Dict[str, Any] = {"url": url}
            if metadata is not None:
                request_kwargs["metadata"] = metadata
            if enable_segment_thumbnails is not None:
                request_kwargs["enable_segment_thumbnails"] = enable_segment_thumbnails
            request = SyncFileFromUrlRequest(**request_kwargs)

            response = self.api.sync_file_from_url(sync_file_from_url_request=request)

            # If not waiting for completion, return immediately
            if not wait_until_finish:
                return response

            # Otherwise poll until completion or timeout
            file_id = response.id
            elapsed = 0
            terminal_states = ["ready", "completed", "failed", "not_applicable"]

            while elapsed < timeout:
                status = self.get(file_id=file_id)

                if status.status in terminal_states:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"File processing did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        status: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[Union[SearchFilter, Dict[str, Any]]] = None,
    ):
        """List available files.

        Args:
            status: Optional filter by file status ('processing', 'ready', 'failed').
            created_before: Optional filter by files created before a specific date, YYYY-MM-DD format in UTC
            created_after: Optional filter by files created after a specific date, YYYY-MM-DD format in UTC
            limit: Optional maximum number of files to return (default 50, max 100).
            offset: Optional number of files to skip.
            order: Optional field to sort by ('created_at', 'filename'). Defaults to 'created_at'.
            sort: Optional sort direction ('asc', 'desc'). Defaults to 'desc'.
            filter: Optional filter object or dictionary for advanced filtering by metadata, video info, or file properties.
                   Use Files.create_filter() to create filter objects.

        Returns:
            A list of file objects.

        Raises:
            CloudglueError: If there is an error listing files or processing the request.
        """
        try:
            # Convert filter dict to SearchFilter object if needed
            filter_obj = None
            if filter is not None:
                if isinstance(filter, dict):
                    # Convert dict to SearchFilter object
                    filter_obj = SearchFilter(**filter)
                else:
                    filter_obj = filter

            return self.api.list_files(
                status=status,
                created_before=created_before,
                created_after=created_after,
                limit=limit,
                offset=offset,
                order=order,
                sort=sort,
                filter=json.dumps(filter_obj.to_dict()) if filter_obj else None,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, file_id: str):
        """Get details about a specific file.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            The file object.

        Raises:
            CloudglueError: If there is an error retrieving the file or processing the request.
        """
        try:
            return self.api.get_file(file_id=file_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def sync_source_metadata(self, file_id: str):
        """Refresh a connector file's source metadata.

        Re-fetches the file's `source_metadata` live from its data connector
        (google-drive, dropbox, zoom, gong, recall, grain, or iconik) and
        updates the stored value. If the file belongs to any metadata
        collections, their search documents are re-indexed with the refreshed
        metadata. Works for both metadata-only and fully ingested connector
        files. Free — no media is downloaded or processed.

        Args:
            file_id: The ID of the connector-backed file to refresh.

        Returns:
            The file object with refreshed `source_metadata`.

        Raises:
            CloudglueError: If the file has no connector URI, the source does
                not support metadata lookup, or the account has no connector
                of that type (400), or the file is not found (404).
        """
        try:
            return self.api.sync_file_source_metadata(file_id=file_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, file_id: str):
        """Delete a file.

        Args:
            file_id: The ID of the file to delete.

        Returns:
            The deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the file or processing the request.
        """
        try:
            return self.api.delete_file(file_id=file_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def update(
        self,
        file_id: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update a file's filename and/or metadata.

        Args:
            file_id: The ID of the file to update.
            filename: Optional new filename for the file.
            metadata: Optional user-provided metadata about the file.

        Returns:
            The updated file object.

        Raises:
            CloudglueError: If there is an error updating the file or processing the request.
        """
        try:
            # Create the update request object
            file_update = FileUpdate(
                filename=filename,
                metadata=metadata,
            )
            
            return self.api.update_file(file_id=file_id, file_update=file_update)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def create_segmentation(
        self,
        file_id: str,
        segmentation_config: Union[SegmentationConfig, Dict[str, Any]],
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Create a new segmentation for a file.

        Args:
            file_id: The ID of the file to segment
            segmentation_config: Segmentation configuration (SegmentationConfig object or dictionary)
            thumbnails_config: Optional configuration for segment thumbnails
            wait_until_finish: Whether to wait for the segmentation to complete
            poll_interval: How often to check the segmentation status (in seconds) if waiting
            timeout: Maximum time to wait for processing (in seconds) if waiting

        Returns:
            The created Segmentation object. If wait_until_finish is True, waits for processing
            to complete and returns the final segmentation state.

        Raises:
            CloudglueError: If there is an error creating the segmentation or processing the request.

        Example:
            # Create uniform segmentation
            config = client.segmentations.create_uniform_config(window_seconds=20)
            segmentation = client.files.create_segmentation(
                file_id="file_123",
                segmentation_config=config,
                wait_until_finish=True
            )
        """
        try:            
            # Handle segmentation_config parameter
            if isinstance(segmentation_config, dict):
                segmentation_config = SegmentationConfig.from_dict(segmentation_config)
            elif not isinstance(segmentation_config, SegmentationConfig):
                raise ValueError("segmentation_config must be a SegmentationConfig object or dictionary")

            # Handle thumbnails_config parameter
            thumbnails_config_obj = None
            if thumbnails_config is not None:
                if isinstance(thumbnails_config, dict):
                    thumbnails_config_obj = ThumbnailsConfig.from_dict(thumbnails_config)
                else:
                    thumbnails_config_obj = thumbnails_config

            # Create the request object
            request = CreateFileSegmentationRequest(
                strategy=segmentation_config.strategy,
                uniform_config=segmentation_config.uniform_config,
                shot_detector_config=segmentation_config.shot_detector_config,
                manual_config=segmentation_config.manual_config,
                keyframe_config=segmentation_config.keyframe_config,
                start_time_seconds=segmentation_config.start_time_seconds,
                end_time_seconds=segmentation_config.end_time_seconds,
                thumbnails_config=thumbnails_config_obj,
            )

            response = self.api.create_file_segmentation(
                file_id=file_id,
                create_file_segmentation_request=request,
            )

            # If not waiting for completion, return immediately
            if not wait_until_finish:
                return response

            # Otherwise poll until completion or timeout
            segmentation_id = response.segmentation_id
            elapsed = 0
            terminal_states = ["completed", "failed", "not_applicable"]

            # Import SegmentationsApi here to avoid circular imports            
            segmentations_api = SegmentationsApi(self.api.api_client)

            while elapsed < timeout:
                status = segmentations_api.get_segmentation(segmentation_id=segmentation_id)

                if status.status in terminal_states:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Segmentation processing did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_segmentations(
        self,
        file_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List segmentations for a specific file.

        Args:
            file_id: The ID of the file to list segmentations for
            limit: Maximum number of segmentations to return (max 100)
            offset: Number of segmentations to skip

        Returns:
            A SegmentationList object containing segmentation objects for the file

        Raises:
            CloudglueError: If there is an error listing the segmentations or processing the request.
        """
        try:
            response = self.api.list_file_segmentations(
                file_id=file_id,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_thumbnails(
        self,
        file_id: str,
        is_default: Optional[bool] = None,
        segmentation_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: Optional[str] = None,
    ):
        """
        Get thumbnails for a file.

        Args:
            file_id: The ID of the file
            is_default: Filter thumbnails by default status. If true, will only return the default thumbnail for the file
            segmentation_id: Filter thumbnails by segmentation ID
            limit: Number of thumbnails to return
            offset: Offset from the start of the list
            type: Filter thumbnails by type

        Returns:
            ThumbnailList response
        """
        try:
            response = self.api.get_thumbnails(
                file_id=file_id,
                is_default=is_default,
                segmentation_id=segmentation_id,
                limit=limit,
                offset=offset,
                type=type,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_segments(
        self,
        file_id: str,
        start_time_after: Optional[float] = None,
        end_time_before: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List segments for a file.

        Args:
            file_id: The ID of the file
            start_time_after: Filter segments by start time (seconds)
            end_time_before: Filter segments by end time (seconds)
            limit: Number of segments to return (max 100)
            offset: Offset from the start of the list

        Returns:
            FileSegmentListResponse containing segments

        Raises:
            CloudglueError: If there is an error listing segments.
        """
        try:
            response = self.api.list_file_segments(
                file_id=file_id,
                start_time_after=start_time_after,
                end_time_before=end_time_before,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_frame_extractions(
        self,
        file_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List frame extraction jobs for a file.

        Args:
            file_id: The ID of the file
            limit: Number of frame extractions to return (max 100)
            offset: Offset from the start of the list

        Returns:
            FrameExtractionList containing frame extraction jobs

        Raises:
            CloudglueError: If there is an error listing frame extractions.
        """
        try:
            response = self.api.list_file_frame_extractions(
                file_id=file_id,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def create_frame_extraction(
        self,
        file_id: str,
        strategy: str = "uniform",
        uniform_config: Optional[Union[FrameExtractionUniformConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[FrameExtractionThumbnailsConfig, Dict[str, Any]]] = None,
        start_time_seconds: Optional[float] = None,
        end_time_seconds: Optional[float] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Create a frame extraction job for a file.

        Args:
            file_id: The ID of the file to extract frames from
            strategy: Frame extraction strategy - currently only 'uniform' is supported
            uniform_config: Configuration for uniform frame extraction (frames_per_second, max_width)
            thumbnails_config: Configuration for frame thumbnails (optional)
            start_time_seconds: Start time in seconds to begin extracting frames
            end_time_seconds: End time in seconds to stop extracting frames
            wait_until_finish: Whether to wait for the job to complete
            poll_interval: How often to check the job status (in seconds)
            timeout: Maximum time to wait for the job to complete (in seconds)

        Returns:
            FrameExtraction: The frame extraction job object

        Raises:
            CloudglueError: If there is an error creating the frame extraction job
        """
        try:
            # Convert config dicts to objects if needed
            uniform_config_obj = None
            if uniform_config is not None:
                if isinstance(uniform_config, dict):
                    uniform_config_obj = FrameExtractionUniformConfig(**uniform_config)
                else:
                    uniform_config_obj = uniform_config
            
            thumbnails_config_obj = None
            if thumbnails_config is not None:
                if isinstance(thumbnails_config, dict):
                    thumbnails_config_obj = FrameExtractionThumbnailsConfig(**thumbnails_config)
                else:
                    thumbnails_config_obj = thumbnails_config

            # Create the request object
            request = CreateFileFrameExtractionRequest(
                strategy=strategy,
                uniform_config=uniform_config_obj,
                thumbnails_config=thumbnails_config_obj,
                start_time_seconds=start_time_seconds,
                end_time_seconds=end_time_seconds
            )

            # Create the frame extraction job
            response = self.api.create_file_frame_extraction(
                file_id=file_id,
                create_file_frame_extraction_request=request
            )

            # If wait_until_finish is True, poll until completion
            if wait_until_finish:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Check if the job is complete
                    if hasattr(response, 'status') and response.status in ['completed', 'failed']:
                        break
                    
                    # Wait before checking again
                    time.sleep(poll_interval)
                    
                    # Get updated status
                    try:
                        from cloudglue.client.main import Cloudglue
                        client = Cloudglue()  # This is not ideal but we need access to frames API
                        response = client.frames.get(response.id)
                    except Exception:
                        # If we can't get status, just return what we have
                        break
                        
                # Check if we timed out
                if hasattr(response, 'status') and response.status not in ['completed', 'failed']:
                    raise CloudglueError(f"Frame extraction job timed out after {timeout} seconds")

            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

