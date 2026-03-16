# cloudglue/client/resources/describe.py
"""Describe resource for Cloudglue API."""
import time
from typing import Dict, Any, List, Optional, Union

from cloudglue.sdk.models.new_describe import NewDescribe
from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.thumbnails_config import ThumbnailsConfig
from cloudglue.sdk.models.update_describe_request import UpdateDescribeRequest
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Describe:
    """Handles media description operations."""

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        url: str,
        enable_summary: bool = True,
        enable_speech: bool = True,
        enable_scene_text: bool = True,
        enable_visual_scene_description: bool = True,
        enable_audio_description: bool = True,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
    ):
        """Create a new media description job for a video.

        Args:
            url: Input video URL. Can be YouTube URLs or URIs of uploaded files.
            enable_summary: Whether to generate video-level and segment-level summaries and titles.
            enable_speech: Whether to generate speech transcript.
            enable_scene_text: Whether to generate scene text extraction.
            enable_visual_scene_description: Whether to generate visual scene description.
            enable_audio_description: Whether to generate audio description.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails

        Returns:
            The typed Describe job object with job_id and status.

        Raises:
            CloudglueError: If there is an error creating the describe job or processing the request.
        """
        try:
            if segmentation_id and segmentation_config:
                raise ValueError("Cannot provide both segmentation_id and segmentation_config")

            # Handle segmentation_config parameter
            if isinstance(segmentation_config, dict):
                segmentation_config = SegmentationConfig.from_dict(segmentation_config)

            # Handle thumbnails_config parameter
            thumbnails_config_obj = None
            if thumbnails_config is not None:
                if isinstance(thumbnails_config, dict):
                    thumbnails_config_obj = ThumbnailsConfig.from_dict(thumbnails_config)
                else:
                    thumbnails_config_obj = thumbnails_config

            request = NewDescribe(
                url=url,
                enable_summary=enable_summary,
                enable_speech=enable_speech,
                enable_scene_text=enable_scene_text,
                enable_visual_scene_description=enable_visual_scene_description,
                enable_audio_description=enable_audio_description,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
                thumbnails_config=thumbnails_config_obj,
            )

            # Use the regular SDK method to create the job
            response = self.api.create_describe(new_describe=request)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(
        self,
        job_id: str,
        response_format: Optional[str] = None,
        start_time_seconds: Optional[float] = None,
        end_time_seconds: Optional[float] = None,
        modalities: Optional[List[str]] = None,
        include_thumbnails: Optional[bool] = None,
        include_word_timestamps: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
    ):
        """Get the status and data of a media description job.

        Args:
            job_id: The unique identifier of the description job.
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            start_time_seconds: The start time in seconds to filter the media descriptions
            end_time_seconds: The end time in seconds to filter the media descriptions
            modalities: Filter results by modality types (e.g., ['speech', 'visual_scene_description'])
            include_thumbnails: When true, include thumbnail_url on the response and segment_summary entries
            include_word_timestamps: When true, include word-level timestamps on speech entries. Not available for YouTube sources. Only applies when response_format=json.
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')

        Returns:
            The typed Describe job object with current status and data (if completed).

        Raises:
            CloudglueError: If there is an error retrieving the describe job or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_describe(
                job_id=job_id,
                response_format=response_format,
                start_time_seconds=start_time_seconds,
                end_time_seconds=end_time_seconds,
                modalities=modalities,
                include_thumbnails=include_thumbnails,
                include_word_timestamps=include_word_timestamps,
                include_chapters=include_chapters,
                include_shots=include_shots,
            )
            return response
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
        response_format: Optional[str] = None,
        url: Optional[str] = None,
        include_data: Optional[bool] = None,
    ):
        """List all media description jobs with optional filtering.

        Args:
            limit: Maximum number of description jobs to return.
            offset: Number of description jobs to skip.
            status: Filter description jobs by status.
            created_before: Filter description jobs created before a specific date (YYYY-MM-DD format), in UTC timezone.
            created_after: Filter description jobs created after a specific date (YYYY-MM-DD format), in UTC timezone.
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            url: Filter description jobs by the input URL used for description.
            include_data: Include the data in the response. If false, the response will only include
                the job information and not the data to minimize the response size.

        Returns:
            The typed DescribeList object with array of describe jobs.

        Raises:
            CloudglueError: If there is an error retrieving the describe jobs or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.list_describes(
                limit=limit,
                offset=offset,
                status=status,
                created_before=created_before,
                created_after=created_after,
                response_format=response_format,
                url=url,
                include_data=include_data,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, job_id: str):
        """Delete a media description job.

        Args:
            job_id: The unique identifier of the description job to delete.

        Returns:
            The deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the description job.
        """
        try:
            response = self.api.delete_describe(job_id=job_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def update(
        self,
        job_id: str,
        use_in_default_index: bool,
    ):
        """Update a describe job.

        Toggle the use_in_default_index flag on an existing describe job.
        Enabling this makes the file searchable by default in the deep search
        and response APIs.

        Args:
            job_id: The unique identifier of the description job.
            use_in_default_index: When True, the video's search documents will be
                added to the account's default index. When False, existing default
                index search documents are removed.

        Returns:
            The updated Describe job object.

        Raises:
            CloudglueError: If there is an error updating the describe job.
        """
        try:
            request = UpdateDescribeRequest(use_in_default_index=use_in_default_index)
            return self.api.update_describe(
                job_id=job_id,
                update_describe_request=request,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def run(
        self,
        url: str,
        poll_interval: int = 5,
        timeout: int = 600,
        enable_summary: bool = True,
        enable_speech: bool = True,
        enable_scene_text: bool = True,
        enable_visual_scene_description: bool = True,
        enable_audio_description: bool = False,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
        response_format: Optional[str] = None,
        modalities: Optional[List[str]] = None,
        include_thumbnails: Optional[bool] = None,
        include_word_timestamps: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
    ):
        """Create a media description job and wait for it to complete.

        Args:
            url: Input video URL. Can be YouTube URLs or URIs of uploaded files.
            poll_interval: Seconds between status checks.
            timeout: Total seconds to wait before giving up.
            enable_summary: Whether to generate video-level and segment-level summaries and titles.
            enable_speech: Whether to generate speech transcript.
            enable_scene_text: Whether to generate scene text extraction.
            enable_visual_scene_description: Whether to generate visual scene description.
            enable_audio_description: Whether to generate audio description.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            modalities: Filter results by modality types (e.g., ['speech', 'visual_scene_description'])
            include_thumbnails: When true, include thumbnail_url on the response and segment_summary entries
            include_word_timestamps: When true, include word-level timestamps on speech entries. Not available for YouTube sources. Only applies when response_format=json.
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')

        Returns:
            The completed typed Describe job object.

        Raises:
            CloudglueError: If there is an error creating or processing the describe job.
        """
        try:
            # Create the job
            job = self.create(
                url=url,
                enable_summary=enable_summary,
                enable_speech=enable_speech,
                enable_scene_text=enable_scene_text,
                enable_visual_scene_description=enable_visual_scene_description,
                enable_audio_description=enable_audio_description,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
                thumbnails_config=thumbnails_config,
            )

            job_id = job.job_id

            # Poll for completion
            elapsed = 0
            while elapsed < timeout:
                status = self.get(job_id=job_id, response_format=response_format, modalities=modalities, include_thumbnails=include_thumbnails, include_word_timestamps=include_word_timestamps, include_chapters=include_chapters, include_shots=include_shots)

                if status.status in ["completed", "failed"]:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Describe job did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

