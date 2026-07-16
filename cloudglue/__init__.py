# cloudglue/__init__.py

from cloudglue._version import __version__

# Import and re-export the client
from cloudglue.client.main import Cloudglue
from cloudglue.client.resources import CloudglueError

# Re-export key models from the SDK
from cloudglue.sdk.models.chat_completion_request import ChatCompletionRequest
from cloudglue.sdk.models.chat_completion_response import ChatCompletionResponse
from cloudglue.sdk.models.chat_completion_request_filter import ChatCompletionRequestFilter
from cloudglue.sdk.models.chat_completion_request_filter_metadata_inner import ChatCompletionRequestFilterMetadataInner
from cloudglue.sdk.models.chat_completion_request_filter_video_info_inner import ChatCompletionRequestFilterVideoInfoInner
from cloudglue.sdk.models.chat_completion_request_filter_file_inner import ChatCompletionRequestFilterFileInner
from cloudglue.sdk.models.file_update import FileUpdate

# Provider source metadata attached to connector-synced files
# (file.source_metadata) and returned by data_connectors.get_source_metadata()
from cloudglue.sdk.models.source_metadata import SourceMetadata
from cloudglue.sdk.models.source_metadata_response import SourceMetadataResponse
from cloudglue.sdk.models.grain_source_metadata import GrainSourceMetadata
from cloudglue.sdk.models.zoom_source_metadata import ZoomSourceMetadata
from cloudglue.sdk.models.recall_source_metadata import RecallSourceMetadata
from cloudglue.sdk.models.google_drive_source_metadata import GoogleDriveSourceMetadata
from cloudglue.sdk.models.dropbox_source_metadata import DropboxSourceMetadata
from cloudglue.sdk.models.gong_source_metadata import GongSourceMetadata

# Export key classes at the module level for clean imports
__all__ = [
    "Cloudglue",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ChatCompletionRequestFilter",
    "ChatCompletionRequestFilterMetadataInner",
    "ChatCompletionRequestFilterVideoInfoInner",
    "ChatCompletionRequestFilterFileInner",
    "FileUpdate",
    "CloudglueError",
    "SourceMetadata",
    "SourceMetadataResponse",
    "GrainSourceMetadata",
    "ZoomSourceMetadata",
    "RecallSourceMetadata",
    "GoogleDriveSourceMetadata",
    "DropboxSourceMetadata",
    "GongSourceMetadata",
]
