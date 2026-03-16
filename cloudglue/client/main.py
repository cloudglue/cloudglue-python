# cloudglue/client/main.py
from typing import Optional
import os

# Import from the generated SDK
from cloudglue.sdk.api.chat_api import ChatApi
from cloudglue.sdk.api.collections_api import CollectionsApi
from cloudglue.sdk.api.transcribe_api import TranscribeApi
from cloudglue.sdk.api.describe_api import DescribeApi
from cloudglue.sdk.api.extract_api import ExtractApi
from cloudglue.sdk.api.files_api import FilesApi
from cloudglue.sdk.api.segmentations_api import SegmentationsApi
from cloudglue.sdk.api.segments_api import SegmentsApi
from cloudglue.sdk.api.search_api import SearchApi
from cloudglue.sdk.api.thumbnails_api import ThumbnailsApi
from cloudglue.sdk.api.frames_api import FramesApi
from cloudglue.sdk.api.face_detection_api import FaceDetectionApi
from cloudglue.sdk.api.face_match_api import FaceMatchApi
from cloudglue.sdk.api.tags_api import TagsApi
from cloudglue.sdk.api.file_segments_api import FileSegmentsApi
from cloudglue.sdk.api.response_api import ResponseApi
from cloudglue.sdk.api.share_api import ShareApi
from cloudglue.sdk.api.data_connectors_api import DataConnectorsApi
from cloudglue.sdk.api.deep_search_api import DeepSearchApi
from cloudglue.sdk.configuration import Configuration
from cloudglue.sdk.api_client import ApiClient

# Import resource classes from the resources package
from cloudglue.client.resources import (
    Chat,
    Files,
    Transcribe,
    Describe,
    Extract,
    Collections,
    Segmentations,
    Segments,
    Search,
    Thumbnails,
    Frames,
    FaceDetection,
    FaceMatch,
    Tags,
    FileSegments,
    Responses,
    Share,
    DataConnectors,
    DeepSearch,
)
from cloudglue._version import __version__

# SDK client constants
SDK_CLIENT_NAME = "cloudglue-python"


class Cloudglue:
    """Main client for interacting with the Cloudglue API."""

    def __init__(
        self, api_key: Optional[str] = None, host: str = "https://api.cloudglue.dev/v1"
    ):
        """Initialize the Cloudglue client.

        Args:
            api_key: Your API key. If not provided, will try to use CLOUDGLUE_API_KEY env variable.
            host: API host to connect to.
        """
        self.api_key = api_key or os.environ.get("CLOUDGLUE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument or via CLOUDGLUE_API_KEY environment variable"
            )

        # Set up configuration
        self.configuration = Configuration(host=host, access_token=self.api_key)
        self.api_client = ApiClient(self.configuration)
        
        # Set custom SDK headers
        self.api_client.set_default_header('x-sdk-client', SDK_CLIENT_NAME)
        self.api_client.set_default_header('x-sdk-version', __version__)

        # Initialize the specific API clients
        self.chat_api = ChatApi(self.api_client)
        self.collections_api = CollectionsApi(self.api_client)
        self.transcribe_api = TranscribeApi(self.api_client)
        self.describe_api = DescribeApi(self.api_client)
        self.extract_api = ExtractApi(self.api_client)
        self.files_api = FilesApi(self.api_client)
        self.segmentations_api = SegmentationsApi(self.api_client)
        self.segments_api = SegmentsApi(self.api_client)
        self.search_api = SearchApi(self.api_client)
        self.thumbnails_api = ThumbnailsApi(self.api_client)
        self.frames_api = FramesApi(self.api_client)
        self.face_detection_api = FaceDetectionApi(self.api_client)
        self.face_match_api = FaceMatchApi(self.api_client)
        self.tags_api = TagsApi(self.api_client)
        self.file_segments_api = FileSegmentsApi(self.api_client)
        self.response_api = ResponseApi(self.api_client)
        self.share_api = ShareApi(self.api_client)
        self.data_connectors_api = DataConnectorsApi(self.api_client)
        self.deep_search_api = DeepSearchApi(self.api_client)

        # Set up resources with their respective API clients
        self.chat = Chat(self.chat_api)
        self.files = Files(self.files_api)
        self.transcribe = Transcribe(self.transcribe_api)
        self.describe = Describe(self.describe_api)
        self.extract = Extract(self.extract_api)
        self.collections = Collections(self.collections_api)
        self.segmentations = Segmentations(self.segmentations_api)
        self.segments = Segments(self.segments_api)
        self.search = Search(self.search_api)
        self.thumbnails = Thumbnails(self.thumbnails_api)
        self.frames = Frames(self.frames_api)
        self.face_detection = FaceDetection(self.face_detection_api)
        self.face_match = FaceMatch(self.face_match_api)
        self.tags = Tags(self.tags_api)
        self.file_segments = FileSegments(self.file_segments_api)
        self.responses = Responses(self.response_api)
        self.share = Share(self.share_api)
        self.data_connectors = DataConnectors(self.data_connectors_api)
        self.deep_search = DeepSearch(self.deep_search_api)

    def close(self):
        """Close the API client."""
        if hasattr(self, "api_client") and self.api_client:
            self.api_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
