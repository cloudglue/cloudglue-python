# cloudglue/client/resources/segmentations.py
"""Segmentations resource for Cloudglue API."""
from typing import List, Dict, Any, Optional, Union

from cloudglue.sdk.models.segmentation_config import SegmentationConfig
from cloudglue.sdk.models.segmentation_uniform_config import SegmentationUniformConfig
from cloudglue.sdk.models.segmentation_shot_detector_config import SegmentationShotDetectorConfig
from cloudglue.sdk.models.segmentation_manual_config import SegmentationManualConfig
from cloudglue.sdk.models.segmentation_manual_config_segments_inner import SegmentationManualConfigSegmentsInner
from cloudglue.sdk.models.narrative_config import NarrativeConfig
from cloudglue.sdk.models.keyframe_config import KeyframeConfig
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Segmentations:
    """Client for the Cloudglue Segmentations API."""

    def __init__(self, api):
        """Initialize the Segmentations client.

        Args:
            api: The SegmentationsApi instance.
        """
        self.api = api

    @staticmethod
    def create_keyframe_config(
        frames_per_segment: Union[int, float],
        max_width: Optional[Union[int, float]] = 280,
    ) -> KeyframeConfig:
        """Create a keyframe extraction configuration.

        Args:
            frames_per_segment: The number of key frames to extract per segment (0-8)
            max_width: The maximum width of the key frames in pixels (144-4320, default 280)

        Returns:
            KeyframeConfig object

        Example:
            # Extract 3 keyframes per segment
            keyframe_config = client.segmentations.create_keyframe_config(frames_per_segment=3)
            
            # Create segmentation with keyframes
            config = client.segmentations.create_uniform_config(
                window_seconds=20,
                keyframe_config=keyframe_config
            )
        """
        return KeyframeConfig(
            frames_per_segment=frames_per_segment,
            max_width=max_width,
        )

    @staticmethod
    def create_uniform_config(
        window_seconds: Union[int, float],
        hop_seconds: Optional[Union[int, float]] = None,
        start_time_seconds: Optional[Union[int, float]] = None,
        end_time_seconds: Optional[Union[int, float]] = None,
        keyframe_config: Optional[Union[KeyframeConfig, Dict[str, Any]]] = None,
    ) -> SegmentationConfig:
        """Create a uniform segmentation configuration.

        Args:
            window_seconds: The duration of each segment in seconds (2-60)
            hop_seconds: The offset between the start of new windows. Defaults to window_seconds if not provided
            start_time_seconds: Optional start time of the video in seconds to start segmenting from
            end_time_seconds: Optional end time of the video in seconds to stop segmenting at
            keyframe_config: Optional configuration for keyframe extraction (not supported for YouTube videos)

        Returns:
            SegmentationConfig configured for uniform segmentation

        Example:
            # 20-second segments with no overlap
            config = client.segmentations.create_uniform_config(window_seconds=20)
            
            # 30-second segments with 15-second overlap
            config = client.segmentations.create_uniform_config(
                window_seconds=30, 
                hop_seconds=15
            )
            
            # With keyframe extraction
            config = client.segmentations.create_uniform_config(
                window_seconds=20,
                keyframe_config=client.segmentations.create_keyframe_config(frames_per_segment=3)
            )
        """
        uniform_config = SegmentationUniformConfig(
            window_seconds=window_seconds,
            hop_seconds=hop_seconds,
        )
        
        # Handle keyframe_config parameter
        keyframe_config_obj = None
        if keyframe_config is not None:
            if isinstance(keyframe_config, dict):
                keyframe_config_obj = KeyframeConfig.from_dict(keyframe_config)
            else:
                keyframe_config_obj = keyframe_config
        
        return SegmentationConfig(
            strategy="uniform",
            uniform_config=uniform_config,
            start_time_seconds=start_time_seconds,
            end_time_seconds=end_time_seconds,
            keyframe_config=keyframe_config_obj,
        )

    @staticmethod
    def create_shot_detector_config(
        detector: str,
        threshold: Optional[Union[int, float]] = None,
        min_seconds: Optional[Union[int, float]] = None,
        max_seconds: Optional[Union[int, float]] = None,
        start_time_seconds: Optional[Union[int, float]] = None,
        end_time_seconds: Optional[Union[int, float]] = None,
        keyframe_config: Optional[Union[KeyframeConfig, Dict[str, Any]]] = None,
        fill_gaps: Optional[bool] = None,
    ) -> SegmentationConfig:
        """Create a shot detector segmentation configuration.

        Args:
            detector: The detector strategy ('adaptive' for dynamic footage, 'content' for controlled footage)
            threshold: Detection sensitivity threshold (lower values create more segments)
            min_seconds: The minimum length of a shot in seconds (1-600)
            max_seconds: The maximum length of a shot in seconds (1-600)
            start_time_seconds: Optional start time of the video in seconds to start segmenting from
            end_time_seconds: Optional end time of the video in seconds to stop segmenting at
            keyframe_config: Optional configuration for keyframe extraction (not supported for YouTube videos)
            fill_gaps: When true, gaps between detected shots are filled. Defaults to true.

        Returns:
            SegmentationConfig configured for shot detection

        Example:
            # Adaptive detector for dynamic content
            config = client.segmentations.create_shot_detector_config(
                detector="adaptive",
                threshold=3.0,
                min_seconds=5,
                max_seconds=30
            )
            
            # Content detector for controlled footage
            config = client.segmentations.create_shot_detector_config(
                detector="content",
                threshold=27.0
            )
        """
        shot_detector_config = SegmentationShotDetectorConfig(
            detector=detector,
            threshold=threshold,
            min_seconds=min_seconds,
            max_seconds=max_seconds,
            fill_gaps=fill_gaps,
        )
        
        # Handle keyframe_config parameter
        keyframe_config_obj = None
        if keyframe_config is not None:
            if isinstance(keyframe_config, dict):
                keyframe_config_obj = KeyframeConfig.from_dict(keyframe_config)
            else:
                keyframe_config_obj = keyframe_config
        
        return SegmentationConfig(
            strategy="shot-detector",
            shot_detector_config=shot_detector_config,
            start_time_seconds=start_time_seconds,
            end_time_seconds=end_time_seconds,
            keyframe_config=keyframe_config_obj,
        )

    @staticmethod
    def create_manual_config(
        segments: List[Dict[str, Union[int, float]]],
    ) -> SegmentationConfig:
        """Create a manual segmentation configuration.

        Args:
            segments: List of segment definitions, each containing:
                - start_time: Start time of the segment in seconds
                - end_time: End time of the segment in seconds

        Returns:
            SegmentationConfig configured for manual segmentation

        Example:
            # Manual segmentation with specific time ranges
            config = client.segmentations.create_manual_config(
                segments=[
                    {"start_time": 0, "end_time": 30},
                    {"start_time": 30, "end_time": 60},
                    {"start_time": 60, "end_time": 90}
                ]
            )
        """
        # Convert dict segments to SegmentationManualConfigSegmentsInner objects
        segment_objects = [
            SegmentationManualConfigSegmentsInner(
                start_time=seg.get("start_time"),
                end_time=seg.get("end_time")
            )
            for seg in segments
        ]

        manual_config = SegmentationManualConfig(
            segments=segment_objects,
        )

        return SegmentationConfig(
            strategy="manual",
            manual_config=manual_config,
        )

    @staticmethod
    def create_narrative_config(
        strategy: Optional[str] = "balanced",
        prompt: Optional[str] = None,
        number_of_chapters: Optional[int] = None,
        min_chapters: Optional[int] = None,
        max_chapters: Optional[int] = None,
        start_time_seconds: Optional[Union[int, float]] = None,
        end_time_seconds: Optional[Union[int, float]] = None,
        keyframe_config: Optional[Union[KeyframeConfig, Dict[str, Any]]] = None,
    ) -> SegmentationConfig:
        """Create a narrative segmentation configuration.

        Narrative segmentation uses AI to identify logical chapter boundaries based on
        content, topics, and narrative flow rather than fixed time intervals or visual changes.

        Args:
            strategy: Narrative segmentation strategy:

                - ``comprehensive``: Uses a VLM to deeply analyze logical segments of video.
                  Only available for video files (not YouTube or audio).
                - ``balanced`` (default): Balanced analysis approach using multiple modalities.
                  Supports YouTube URLs and audio files.
                - ``transcript``: Cheap and fast speech-transcript-based segmentation. Requires
                  a transcript; returns an error for silent or visual-only content (use
                  ``balanced`` instead, or ``comprehensive`` for non-YouTube/non-audio video
                  files).

                YouTube URLs and audio files only support ``balanced`` and ``transcript``;
                ``comprehensive`` will be rejected with an error.
            prompt: Optional custom prompt to guide the narrative segmentation analysis.
                This will be incorporated into the main segmentation prompt as additional guidance.
            number_of_chapters: Optional target number of chapters to generate.
                If provided, min_chapters and max_chapters will be calculated automatically if not specified.
            min_chapters: Optional minimum number of chapters to generate.
            max_chapters: Optional maximum number of chapters to generate.
            start_time_seconds: Optional start time of the video in seconds to start segmenting from
            end_time_seconds: Optional end time of the video in seconds to stop segmenting at
            keyframe_config: Optional configuration for keyframe extraction (not supported for YouTube videos)

        Returns:
            SegmentationConfig configured for narrative segmentation

        Example:
            # Basic narrative segmentation with balanced strategy
            config = client.segmentations.create_narrative_config()

            # Comprehensive strategy for detailed video analysis
            config = client.segmentations.create_narrative_config(
                strategy="comprehensive",
                number_of_chapters=5
            )

            # With custom prompt guidance
            config = client.segmentations.create_narrative_config(
                prompt="Focus on topic changes and speaker transitions",
                min_chapters=3,
                max_chapters=10
            )
        """
        narrative_config = NarrativeConfig(
            strategy=strategy,
            prompt=prompt,
            number_of_chapters=number_of_chapters,
            min_chapters=min_chapters,
            max_chapters=max_chapters,
        )

        # Handle keyframe_config parameter
        keyframe_config_obj = None
        if keyframe_config is not None:
            if isinstance(keyframe_config, dict):
                keyframe_config_obj = KeyframeConfig.from_dict(keyframe_config)
            else:
                keyframe_config_obj = keyframe_config

        return SegmentationConfig(
            strategy="narrative",
            narrative_config=narrative_config,
            start_time_seconds=start_time_seconds,
            end_time_seconds=end_time_seconds,
            keyframe_config=keyframe_config_obj,
        )

    def get(
        self,
        segmentation_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """Get a specific segmentation including its segments.

        Args:
            segmentation_id: The ID of the segmentation to retrieve
            limit: Number of segments to return (max 100)
            offset: Offset from the start of the segments list

        Returns:
            The typed Segmentation object with segments and metadata

        Raises:
            CloudglueError: If there is an error retrieving the segmentation or processing the request.
        """
        try:
            response = self.api.get_segmentation(
                segmentation_id=segmentation_id,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, segmentation_id: str):
        """Delete a segmentation.

        Args:
            segmentation_id: The ID of the segmentation to delete

        Returns:
            The deletion confirmation

        Raises:
            CloudglueError: If there is an error deleting the segmentation or processing the request.
        """
        try:
            response = self.api.delete_segmentation(segmentation_id=segmentation_id)
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get_thumbnails(
        self,
        segmentation_id: str,
        segment_ids: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """
        Get thumbnails for a segmentation.

        Args:
            segmentation_id: The ID of the segmentation to retrieve thumbnails for
            segment_ids: Filter thumbnails by segment IDs. If provided, will only return thumbnails for the specified segments. Comma separated list of segment IDs.
            limit: Number of thumbnails to return
            offset: Offset from the start of the list

        Returns:
            ThumbnailList response
        """
        try:
            response = self.api.get_segmentation_thumbnails(
                segmentation_id=segmentation_id,
                segment_ids=segment_ids,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list_describes(
        self,
        segmentation_id: str,
        include_data: Optional[bool] = None,
        response_format: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        """List describe jobs for a segmentation.

        List all describe jobs that referenced the specified segmentation.
        Returns describe job records associated with the segmentation.

        Args:
            segmentation_id: The ID of the segmentation job
            include_data: Include the describe data in the response. Defaults to false.
            response_format: Output format for the describe data ('json' or 'markdown')
            limit: Number of items to return (max 100)
            offset: Offset from the start of the list

        Returns:
            DescribeList containing describe jobs for the segmentation

        Raises:
            CloudglueError: If there is an error listing describes.
        """
        try:
            response = self.api.list_segmentation_describes(
                segmentation_id=segmentation_id,
                include_data=include_data,
                response_format=response_format,
                limit=limit,
                offset=offset,
            )
            return response
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

