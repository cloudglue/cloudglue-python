# cloudglue/client/resources/extract.py
"""Extract resource for Cloudglue API."""
import time
from typing import Dict, Any, Optional, Union

from cloudglue.sdk.models.new_extract import NewExtract
from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.thumbnails_config import ThumbnailsConfig
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Extract:
    """Client for the Cloudglue Extract API."""

    def __init__(self, api):
        """Initialize the Extract client.

        Args:
            api: The DefaultApi instance.
        """
        self.api = api

    def create(
        self,
        url: str,
        prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        enable_video_level_entities: Optional[bool] = None,
        enable_segment_level_entities: Optional[bool] = None,
        enable_transcript_mode: Optional[bool] = None,
        enable_metadata_mode: Optional[bool] = None,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
    ):
        """Create a new extraction job.

        Args:
            url: The URL of the media to extract data from. Can be a YouTube URL,
                a cloudglue file URI (video, audio, or image), or a public direct
                image URL (JPEG/PNG/WebP).
            prompt: A natural language description of what to extract. Required if schema is not provided.
            schema: A JSON schema defining the structure of the data to extract. Required if prompt is not provided.
            enable_video_level_entities: Whether to extract entities at the video level
            enable_segment_level_entities: Whether to extract entities at the segment level
            enable_transcript_mode: When enabled, extract entities from the transcript
                instead of the media content. Mutually exclusive with enable_metadata_mode.
            enable_metadata_mode: When enabled, extract entities from the file's
                metadata document (filename, file details, user metadata, and connector
                source metadata) instead of the media content. File-level entities only;
                flat 1 credit per file; works on metadata-only files without ingesting
                their media. Mutually exclusive with enable_transcript_mode.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails

        Returns:
            Extract: A typed Extract object containing job_id, status, and other fields.

        Raises:
            CloudglueError: If there is an error creating the extraction job or processing the request.
        """
        try:
            if not prompt and not schema:
                raise ValueError("Either prompt or schema must be provided")

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

            # Set up the request object
            request = NewExtract(
                url=url,
                prompt=prompt,
                var_schema=schema,
                enable_video_level_entities=enable_video_level_entities,
                enable_segment_level_entities=enable_segment_level_entities,
                enable_transcript_mode=enable_transcript_mode,
                enable_metadata_mode=enable_metadata_mode,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
                thumbnails_config=thumbnails_config_obj,
            )

            # Use the standard method to get a properly typed Extract object
            response = self.api.create_extract(new_extract=request)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(
        self,
        job_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include_thumbnails: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
        ):
        """Get the status of an extraction job.

        Args:
            job_id: The ID of the extraction job.
            limit: Maximum number of segment entities to return (1-100)
            offset: Number of segment entities to skip
            include_thumbnails: When true, include thumbnail_url on the data object and segment entities
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')
        Returns:
            Extract: A typed Extract object containing the job status and extracted data if available.

        Raises:
            CloudglueError: If there is an error retrieving the extraction job or processing the request.
        """
        try:
            response = self.api.get_extract(job_id=job_id, limit=limit, offset=offset, include_thumbnails=include_thumbnails, include_chapters=include_chapters, include_shots=include_shots)
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
        url: Optional[str] = None,
        include_data: Optional[bool] = None,
    ):
        """List extraction jobs.

        Args:
            limit: Maximum number of jobs to return.
            offset: Number of jobs to skip.
            status: Filter by job status.
            created_before: Filter by jobs created before a specific date, YYYY-MM-DD format in UTC.
            created_after: Filter by jobs created after a specific date, YYYY-MM-DD format in UTC.
            url: Filter by jobs with a specific URL.
            include_data: Include the data in the response. If false, the response will only include
                the job information and not the data to minimize the response size.

        Returns:
            A list of extraction jobs.

        Raises:
            CloudglueError: If there is an error listing the extraction jobs or processing the request.
        """
        try:
            return self.api.list_extracts(
                limit=limit,
                offset=offset,
                status=status,
                created_before=created_before,
                created_after=created_after,
                url=url,
                include_data=include_data,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, job_id: str):
        """Delete an extraction job.

        Args:
            job_id: The unique identifier of the extraction job to delete.

        Returns:
            The deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the extraction job.
        """
        try:
            response = self.api.delete_extract(job_id=job_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def run(
        self,
        url: str,
        prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        enable_video_level_entities: Optional[bool] = None,
        enable_segment_level_entities: Optional[bool] = None,
        enable_transcript_mode: Optional[bool] = None,
        enable_metadata_mode: Optional[bool] = None,
        segmentation_id: Optional[str] = None,
        segmentation_config: Optional[Union[SegmentationConfig, Dict[str, Any]]] = None,
        thumbnails_config: Optional[Union[Dict[str, Any], Any]] = None,
        poll_interval: int = 5,
        timeout: int = 600,
        include_thumbnails: Optional[bool] = None,
        include_chapters: Optional[bool] = None,
        include_shots: Optional[bool] = None,
    ):
        """Create an extraction job and wait for it to complete.

        Args:
            url: The URL of the media to extract data from. Can be a YouTube URL,
                a cloudglue file URI (video, audio, or image), or a public direct
                image URL (JPEG/PNG/WebP).
            prompt: A natural language description of what to extract. Required if schema is not provided.
            schema: A JSON schema defining the structure of the data to extract. Required if prompt is not provided.
            enable_video_level_entities: Whether to extract entities at the video level
            enable_segment_level_entities: Whether to extract entities at the segment level
            enable_transcript_mode: When enabled, extract entities from the transcript
                instead of the media content. Mutually exclusive with enable_metadata_mode.
            enable_metadata_mode: When enabled, extract entities from the file's
                metadata document instead of the media content. File-level entities
                only; flat 1 credit per file; works on metadata-only files. Mutually
                exclusive with enable_transcript_mode.
            segmentation_id: Segmentation job id to use. Cannot be provided together with segmentation_config.
            segmentation_config: Configuration for video segmentation. Cannot be provided together with segmentation_id.
            thumbnails_config: Optional configuration for segment thumbnails
            poll_interval: How often to check the job status (in seconds).
            timeout: Maximum time to wait for the job to complete (in seconds).
            include_thumbnails: When true, include thumbnail_url on the data object and segment entities
            include_chapters: When true, include narrative chapters in the response (when segmentation strategy is 'narrative')
            include_shots: When true, include shot boundaries in the response (when segmentation strategy is 'shot-detector')

        Returns:
            Extract: The completed Extract object with status and data.

        Raises:
            CloudglueError: If there is an error creating or processing the extraction job.
        """
        try:
            # Create the extraction job
            job = self.create(
                url=url,
                prompt=prompt,
                schema=schema,
                enable_video_level_entities=enable_video_level_entities,
                enable_segment_level_entities=enable_segment_level_entities,
                enable_transcript_mode=enable_transcript_mode,
                enable_metadata_mode=enable_metadata_mode,
                segmentation_id=segmentation_id,
                segmentation_config=segmentation_config,
                thumbnails_config=thumbnails_config,
            )
            job_id = job.job_id

            # Poll for completion
            elapsed = 0
            while elapsed < timeout:
                status = self.get(job_id=job_id, include_thumbnails=include_thumbnails, include_chapters=include_chapters, include_shots=include_shots)

                if status.status in ["completed", "failed"]:
                    return status

                time.sleep(poll_interval)
                elapsed += poll_interval

            raise TimeoutError(
                f"Extraction job did not complete within {timeout} seconds"
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

