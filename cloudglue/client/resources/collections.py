# cloudglue/client/resources/collections.py
"""Collections resource for Cloudglue API."""
import json
import time
from typing import Dict, Any, Optional, Union

from cloudglue.sdk.models.new_collection import NewCollection
from cloudglue.sdk.models.add_collection_file import AddCollectionFile
from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.default_segmentation_config import DefaultSegmentationConfig
from cloudglue.sdk.models.search_filter import SearchFilter
from cloudglue.sdk.models.collection_update import CollectionUpdate
from cloudglue.sdk.models.new_collection_face_detection_config import NewCollectionFaceDetectionConfig
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Collections:
    """Client for the Cloudglue Collections API."""

    def __init__(self, api):
        """Initialize the Collections client.

        Args:
            api: The DefaultApi instance.
        """
        self.api = api

    def create(
        self,
        collection_type: str,
        name: str,
        description: Optional[str] = None,
        extract_config: Optional[Dict[str, Any]] = None,
        transcribe_config: Optional[Dict[str, Any]] = None,
        describe_config: Optional[Dict[str, Any]] = None,
        default_segmentation_config: Optional[Union[DefaultSegmentationConfig, SegmentationConfig, Dict[str, Any]]] = None,
        face_detection_config: Optional[Union[NewCollectionFaceDetectionConfig, Dict[str, Any]]] = None,
    ):
        """Create a new collection.

        Args:
            collection_type: Type of collection ('entities', 'rich-transcripts', 'media-descriptions',
                'face-analysis', 'metadata'). 'metadata' collections index connector source metadata
                and user metadata into file-level search documents WITHOUT downloading or processing
                the media — free to index, no processing configs, supports google-drive, dropbox,
                zoom, gong, recall, grain, and iconik URLs.
            name: Name of the collection (must be unique)
            description: Optional description of the collection
            extract_config: Optional configuration for extraction processing
            transcribe_config: Optional configuration for transcription processing
            describe_config: Optional configuration for media description processing
            default_segmentation_config: Default segmentation configuration for files in this collection.
                Can be a DefaultSegmentationConfig, SegmentationConfig (will be converted), or dict.
                Note: Only 'uniform' and 'shot-detector' strategies are supported for collection defaults.
            face_detection_config: Optional configuration for face detection processing

        Returns:
            The typed Collection object with all properties

        Raises:
            CloudglueError: If there is an error creating the collection or processing the request.
        """
        try:
            # Create request object using the SDK model
            if description is None:  # TODO(kdr): temporary fix for API
                description = ""

            # Handle default_segmentation_config parameter - convert to DefaultSegmentationConfig
            if default_segmentation_config is not None:
                if isinstance(default_segmentation_config, dict):
                    default_segmentation_config = DefaultSegmentationConfig.from_dict(default_segmentation_config)
                elif isinstance(default_segmentation_config, SegmentationConfig):
                    # Convert SegmentationConfig to DefaultSegmentationConfig
                    # Note: manual_config is not supported for default segmentation configs
                    default_segmentation_config = DefaultSegmentationConfig(
                        strategy=default_segmentation_config.strategy,
                        uniform_config=default_segmentation_config.uniform_config,
                        shot_detector_config=default_segmentation_config.shot_detector_config,
                        narrative_config=default_segmentation_config.narrative_config,
                        keyframe_config=default_segmentation_config.keyframe_config,
                        start_time_seconds=default_segmentation_config.start_time_seconds,
                        end_time_seconds=default_segmentation_config.end_time_seconds,
                    )

            # Handle face_detection_config parameter
            if isinstance(face_detection_config, dict):
                face_detection_config = NewCollectionFaceDetectionConfig.from_dict(face_detection_config)

            request = NewCollection(
                collection_type=collection_type,
                name=name,
                description=description,
                extract_config=extract_config,
                transcribe_config=transcribe_config,
                describe_config=describe_config,
                default_segmentation_config=default_segmentation_config,
                face_detection_config=face_detection_config,
            )
            # Use the standard method to get a properly typed object
            response = self.api.create_collection(new_collection=request)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        collection_type: Optional[str] = None,
    ):
        """List collections.

        Args:
            limit: Maximum number of collections to return (max 100)
            offset: Number of collections to skip
            order: Field to sort by ('created_at'). Defaults to 'created_at'
            sort: Sort direction ('asc', 'desc'). Defaults to 'desc'
            collection_type: Filter by collection type ('entities', 'rich-transcripts',
                'media-descriptions', 'face-analysis', 'metadata')

        Returns:
            The typed CollectionList object with collections and metadata

        Raises:
            CloudglueError: If there is an error listing collections or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.list_collections(
                limit=limit, offset=offset, order=order, sort=sort, collection_type=collection_type
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, collection_id: str):
        """Get a specific collection by ID.

        Args:
            collection_id: The ID of the collection to retrieve

        Returns:
            The typed Collection object with all properties

        Raises:
            CloudglueError: If there is an error retrieving the collection or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_collection(collection_id=collection_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, collection_id: str):
        """Delete a collection.

        Args:
            collection_id: The ID of the collection to delete

        Returns:
            The typed DeleteResponse object with deletion confirmation

        Raises:
            CloudglueError: If there is an error deleting the collection or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.delete_collection(collection_id=collection_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def update(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Update a collection.

        Args:
            collection_id: The ID of the collection to update
            name: New name for the collection
            description: New description for the collection

        Returns:
            The updated Collection object

        Raises:
            CloudglueError: If there is an error updating the collection or processing the request.
        """
        try:
            # Create update request object
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            
            if not update_data:
                raise CloudglueError("At least one field (name or description) must be provided for update")
            
            collection_update = CollectionUpdate(**update_data)
            response = self.api.update_collection(
                collection_id=collection_id,
                collection_update=collection_update
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def add_video(
        self,
        collection_id: str,
        file_id: Optional[str] = None,
        url: Optional[str] = None,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Add a video file to a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to add to the collection (optional, either file_id or url is required)
            url: The URL of the file to add to the collection (optional, either file_id or url is required)
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            wait_until_finish: Whether to wait for the video processing to complete
            poll_interval: How often to check the video status (in seconds) if waiting
            timeout: Maximum time to wait for processing (in seconds) if waiting

        Returns:
            The typed CollectionFile object with association details. If wait_until_finish
            is True, waits for processing to complete and returns the final video state.

        Raises:
            CloudglueError: If there is an error adding the video or processing the request.
        """
        try:
            # Validate that either file_id or url is provided
            if not file_id and not url:
                raise CloudglueError("Either file_id or url must be provided")
            
            if segmentation_id and segmentation_config:
                raise ValueError("Cannot provide both segmentation_id and segmentation_config")

            # Handle segmentation_config parameter
            if isinstance(segmentation_config, dict):
                segmentation_config = SegmentationConfig.from_dict(segmentation_config)

            # Create request object using the SDK model
            # The post-processing script fixes the generated model to properly handle
            # the oneOf constraint (either file_id or url, not both required)
            request = AddCollectionFile(
                file_id=file_id,
                url=url,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
            )

            # Use the standard method to get a properly typed object
            response = self.api.add_video(
                collection_id=collection_id, add_collection_file=request
            )

            # If not waiting for completion, return immediately
            if not wait_until_finish:
                return response

            # Otherwise poll until completion or timeout
            response_file_id = response.file_id
            elapsed = 0
            terminal_states = ["ready", "completed", "failed", "not_applicable"]

            while elapsed < timeout:
                status = self.get_video(collection_id=collection_id, file_id=response_file_id)

                if status.status in terminal_states:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Video processing did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_video(self, collection_id: str, file_id: str):
        """Get information about a specific video in a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to retrieve

        Returns:
            The typed CollectionFile object with video details

        Raises:
            CloudglueError: If there is an error retrieving the video or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_video(collection_id=collection_id, file_id=file_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_videos(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
        added_before: Optional[str] = None,
        added_after: Optional[str] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[Union[SearchFilter, Dict[str, Any]]] = None,
    ):
        """List videos in a collection.

        Args:
            collection_id: The ID of the collection
            limit: Maximum number of videos to return (max 100)
            offset: Number of videos to skip
            status: Filter by processing status ('pending', 'processing', 'ready', 'failed')
            added_before: Filter by videos added before a specific date, YYYY-MM-DD format in UTC
            added_after: Filter by videos added after a specific date, YYYY-MM-DD format in UTC
            order: Field to sort by ('created_at'). Defaults to 'created_at'
            sort: Sort direction ('asc', 'desc'). Defaults to 'desc'
            filter: Optional filter object or dictionary for advanced filtering by metadata, video info, or file properties.
                   Use Files.create_filter() to create filter objects.
        Returns:
            The typed CollectionFileList object with videos and metadata

        Raises:
            CloudglueError: If there is an error listing the videos or processing the request.
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

            # Use the standard method to get a properly typed object
            response = self.api.list_videos(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
                status=status,
                added_before=added_before,
                added_after=added_after,
                order=order,
                sort=sort,
                filter=json.dumps(filter_obj.to_dict()) if filter_obj else None,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def remove_video(self, collection_id: str, file_id: str):
        """Remove a video from a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to remove

        Returns:
            The typed DeleteResponse object with removal confirmation

        Raises:
            CloudglueError: If there is an error removing the video or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.delete_video(
                collection_id=collection_id, file_id=file_id
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_rich_transcripts(
        self,
        collection_id: str,
        file_id: str,
        start_time_seconds: Optional[float] = None,
        end_time_seconds: Optional[float] = None,
        response_format: Optional[str] = None,
        include_metadata: Optional[bool] = None,
    ):
        """Get the rich transcript of a video in a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to retrieve the rich transcript for
            start_time_seconds: The start time in seconds to filter the rich transcript
            end_time_seconds: The end time in seconds to filter the rich transcript
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            include_metadata: When true, include the file's `metadata` and `source_metadata`
                on the response's `file` object.

        Returns:
            The typed RichTranscript object with video rich transcript data

        Raises:
            CloudglueError: If there is an error retrieving the rich transcript or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_transcripts(
                collection_id=collection_id, file_id=file_id, start_time_seconds=start_time_seconds, end_time_seconds=end_time_seconds, response_format=response_format, include_metadata=include_metadata
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_video_entities(
        self,
        collection_id: str,
        file_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include_thumbnails: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
    ):
        """Get the entities extracted from a video in a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to retrieve entities for
            limit: Maximum number of segment entities to return (1-100)
            offset: Number of segment entities to skip
            include_thumbnails: When true, include thumbnail_url on the response and segment entities
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')

        Returns:
            The typed FileEntities object with video entities data

        Raises:
            CloudglueError: If there is an error retrieving the entities or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_entities(
                collection_id=collection_id,
                file_id=file_id,
                limit=limit,
                offset=offset,
                include_thumbnails=include_thumbnails,
                include_chapters=include_chapters,
                include_shots=include_shots,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_entities(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        added_before: Optional[str] = None,
        added_after: Optional[str] = None,
    ):
        """List all extracted entities for files in a collection.

        This API is only available when a collection is created with collection_type 'entities'.

        Args:
            collection_id: The ID of the collection
            limit: Maximum number of files to return
            offset: Number of files to skip
            order: Order the files by a specific field
            sort: Sort the files in ascending or descending order
            added_before: Filter files added before a specific date (YYYY-MM-DD format), in UTC timezone
            added_after: Filter files added after a specific date (YYYY-MM-DD format), in UTC timezone

        Returns:
            Collection entities list response

        Raises:
            CloudglueError: If the request fails
        """
        try:
            response = self.api.list_collection_entities(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
                order=order,
                sort=sort,
                added_before=added_before,
                added_after=added_after,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(
                f"Failed to list entities in collection {collection_id}: {str(e)}"
            )

    def list_rich_transcripts(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        added_before: Optional[str] = None,
        added_after: Optional[str] = None,
        response_format: Optional[str] = None,
        include_metadata: Optional[bool] = None,
    ):
        """List all rich transcription data for files in a collection.

        This API is only available when a collection is created with collection_type 'rich-transcripts'.

        Args:
            collection_id: The ID of the collection
            limit: Maximum number of files to return
            offset: Number of files to skip
            order: Order the files by a specific field
            sort: Sort the files in ascending or descending order
            added_before: Filter files added before a specific date (YYYY-MM-DD format), in UTC timezone
            added_after: Filter files added after a specific date (YYYY-MM-DD format), in UTC timezone
            response_format: Format for the response
            include_metadata: When true, include each file's `metadata` and `source_metadata`
                on the `file` object of each entry.

        Returns:
            Collection rich transcripts list response

        Raises:
            CloudglueError: If the request fails
        """
        try:
            response = self.api.list_collection_rich_transcripts(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
                order=order,
                sort=sort,
                added_before=added_before,
                added_after=added_after,
                response_format=response_format,
                include_metadata=include_metadata,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(
                f"Failed to list rich transcripts in collection {collection_id}: {str(e)}"
            )

    def get_media_descriptions(
        self,
        collection_id: str,
        file_id: str,
        start_time_seconds: Optional[float] = None,
        end_time_seconds: Optional[float] = None,
        response_format: Optional[str] = None,
        include_thumbnails: Optional[bool] = None,
        include_word_timestamps: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
        include_metadata: Optional[bool] = None,
    ):
        """Get the media descriptions of a video in a collection.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to retrieve the media descriptions for
            start_time_seconds: The start time in seconds to filter the media descriptions
            end_time_seconds: The end time in seconds to filter the media descriptions
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            include_thumbnails: When true, include thumbnail_url on the response and segment_summary entries
            include_word_timestamps: When true, include word-level timestamps on speech entries. Not available for YouTube sources. Only applies when response_format=json.
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')
            include_metadata: When true, include the file's `metadata` and `source_metadata`
                on the response's `file` object.

        Returns:
            The typed MediaDescription object with video media description data

        Raises:
            CloudglueError: If there is an error retrieving the media descriptions or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_media_descriptions(
                collection_id=collection_id, file_id=file_id, start_time_seconds=start_time_seconds, end_time_seconds=end_time_seconds, response_format=response_format, include_thumbnails=include_thumbnails, include_word_timestamps=include_word_timestamps, include_chapters=include_chapters, include_shots=include_shots, include_metadata=include_metadata
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_media_descriptions(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        sort: Optional[str] = None,
        added_before: Optional[str] = None,
        added_after: Optional[str] = None,
        response_format: Optional[str] = None,
        include_metadata: Optional[bool] = None,
    ):
        """List all media description data for files in a collection.

        This API is only available when a collection is created with collection_type 'media-descriptions'.

        Args:
            collection_id: The ID of the collection
            limit: Maximum number of files to return
            offset: Number of files to skip
            order: Order the files by a specific field
            sort: Sort the files in ascending or descending order
            added_before: Filter files added before a specific date (YYYY-MM-DD format), in UTC timezone
            added_after: Filter files added after a specific date (YYYY-MM-DD format), in UTC timezone
            response_format: Format for the response
            include_metadata: When true, include each file's `metadata` and `source_metadata`
                on the `file` object of each entry.

        Returns:
            Collection media descriptions list response

        Raises:
            CloudglueError: If the request fails
        """
        try:
            response = self.api.list_collection_media_descriptions(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
                order=order,
                sort=sort,
                added_before=added_before,
                added_after=added_after,
                response_format=response_format,
                include_metadata=include_metadata,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(
                f"Failed to list media descriptions in collection {collection_id}: {str(e)}"
            )

    def get_face_detections(
        self,
        collection_id: str,
        file_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """Retrieve face detections for a specific file in a collection.

        This API is only available when a collection is created with collection_type 'face-analysis'.

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file
            limit: Maximum number of faces to return (1-100, default 50)
            offset: Number of faces to skip (default 0)

        Returns:
            FileFaceDetections object containing detected faces

        Raises:
            CloudglueError: If the request fails
        """
        try:
            response = self.api.get_face_detections(
                collection_id=collection_id,
                file_id=file_id,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(
                f"Failed to get face detections for file {file_id} in collection {collection_id}: {str(e)}"
            )

    def add_media(
        self,
        collection_id: str,
        file_id: Optional[str] = None,
        url: Optional[str] = None,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        wait_until_finish: bool = False,
        poll_interval: int = 5,
        timeout: int = 600,
    ):
        """Add a media file (video or audio) to a collection.

        This is the recommended endpoint for adding media files to collections.

        Media Type Handling:
        - Video files: Processed with full visual analysis (scene description, text extraction, etc.)
        - Audio files: Visual features automatically disabled; only speech and audio analysis available

        Audio File Restrictions:
        - Audio files cannot be added to face-analysis collections
        - Shot-detector segmentation is not available for audio files

        Args:
            collection_id: The ID of the collection
            file_id: The ID of the file to add (optional, either file_id or url is required)
            url: The URL of the file to add (optional, either file_id or url is required)
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for segmentation. Cannot be provided together with segmentation_id.
            wait_until_finish: Whether to wait for the processing to complete
            poll_interval: How often to check the status (in seconds) if waiting
            timeout: Maximum time to wait for processing (in seconds) if waiting

        Returns:
            The typed CollectionFile object with association details. If wait_until_finish
            is True, waits for processing to complete and returns the final state.

        Raises:
            CloudglueError: If there is an error adding the media or processing the request.
        """
        try:
            # Validate that either file_id or url is provided
            if not file_id and not url:
                raise CloudglueError("Either file_id or url must be provided")

            if segmentation_id and segmentation_config:
                raise ValueError("Cannot provide both segmentation_id and segmentation_config")

            # Handle segmentation_config parameter
            if isinstance(segmentation_config, dict):
                segmentation_config = SegmentationConfig.from_dict(segmentation_config)

            # Create request object
            request = AddCollectionFile(
                file_id=file_id,
                url=url,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
            )

            response = self.api.add_media(
                collection_id=collection_id, add_collection_file=request
            )

            # If not waiting for completion, return immediately
            if not wait_until_finish:
                return response

            # Otherwise poll until completion or timeout
            response_file_id = response.file_id
            elapsed = 0
            terminal_states = ["ready", "completed", "failed", "not_applicable"]

            while elapsed < timeout:
                status = self.get_video(collection_id=collection_id, file_id=response_file_id)

                if status.status in terminal_states:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Media processing did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

