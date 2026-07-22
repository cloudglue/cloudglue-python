# cloudglue/client/resources/transcribe.py
"""Transcribe resource for Cloudglue API."""
import time
from typing import Dict, Any, Optional, Union

from cloudglue.sdk.models.new_transcribe import NewTranscribe
from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.thumbnails_config import ThumbnailsConfig
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Transcribe:
    """Handles rich video transcription operations."""

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        url: str,
        enable_summary: bool = True,
        enable_speech: bool = True,
        enable_scene_text: bool = False,
        enable_visual_scene_description: bool = False,
        enable_audio_description: bool = False,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
    ):
        """Create a new transcribe job for a video.

        Args:
            url: Input video URL. Can be YouTube URLs or URIs of uploaded files.
            enable_summary: Whether to generate a summary of the video.
            enable_speech: Whether to generate speech transcript.
            enable_scene_text: Whether to generate scene text.
            enable_visual_scene_description: Whether to generate visual scene description.
            enable_audio_description: Whether to generate audio description.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails

        Returns:
            The typed Transcribe job object with job_id and status.

        Raises:
            CloudglueError: If there is an error creating the transcribe job or processing the request.
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

            request = NewTranscribe(
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
            response = self.api.create_transcribe(new_transcribe=request)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    # TODO (kdr): asyncio version of this
    def get(
        self,
        job_id: str,
        response_format: Optional[str] = None,
        include_metadata: Optional[bool] = None,
    ):
        """Get the current state of a transcribe job.

        Args:
            job_id: The unique identifier of the transcribe job.
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            include_metadata: When true, include the file's `metadata` and `source_metadata`
                on the response's `file` object.

        Returns:
            The typed Transcribe job object with status and data.

        Raises:
            CloudglueError: If there is an error retrieving the transcribe job or processing the request.
        """
        try:
            # Use the standard method to get a properly typed object
            response = self.api.get_transcribe(
                job_id=job_id,
                response_format=response_format,
                include_metadata=include_metadata,
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
        include_metadata: Optional[bool] = None,
    ):
        """List transcribe jobs.

        Args:
            limit: Maximum number of jobs to return.
            offset: Number of jobs to skip.
            status: Filter by job status.
            created_before: Filter by jobs created before a specific date, YYYY-MM-DD format in UTC.
            created_after: Filter by jobs created after a specific date, YYYY-MM-DD format in UTC.
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
            url: Filter by jobs with a specific URL.
            include_metadata: When true, include each file's `metadata` and `source_metadata`
                on the `file` object of each job.

        Returns:
            A list of transcribe jobs.

        Raises:
            CloudglueError: If there is an error listing the transcribe jobs or processing the request.
        """
        try:
            return self.api.list_transcribes(
                limit=limit,
                offset=offset,
                status=status,
                created_before=created_before,
                created_after=created_after,
                response_format=response_format,
                url=url,
                include_metadata=include_metadata,
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
        enable_scene_text: bool = False,
        enable_visual_scene_description: bool = False,
        enable_audio_description: bool = False,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
        response_format: Optional[str] = None,
    ):
        """Create a transcribe job and wait for it to complete.

        Args:
            url: Input video URL. Can be YouTube URLs or URIs of uploaded files.
            poll_interval: Seconds between status checks.
            timeout: Total seconds to wait before giving up.
            enable_summary: Whether to generate a summary of the video.
            enable_speech: Whether to generate speech transcript.
            enable_scene_text: Whether to generate scene text.
            enable_visual_scene_description: Whether to generate visual scene description.
            enable_audio_description: Whether to generate audio description.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails
            response_format: The format of the response, one of 'json' or 'markdown' (json by default)
        Returns:
            The completed typed Transcribe job object.

        Raises:
            CloudglueError: If there is an error creating or processing the transcribe job.
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
                status = self.get(job_id=job_id, response_format=response_format)

                if status.status in ["completed", "failed"]:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Transcribe job did not complete within {timeout} seconds"
            )

        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

