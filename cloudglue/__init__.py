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
from cloudglue.sdk.models.iconik_source_metadata import IconikSourceMetadata

# Bulk imports (client.bulk_imports)
from cloudglue.sdk.models.metadata_import import MetadataImport
from cloudglue.sdk.models.metadata_import_detail import MetadataImportDetail
from cloudglue.sdk.models.metadata_import_list import MetadataImportList
from cloudglue.sdk.models.metadata_import_run import MetadataImportRun
from cloudglue.sdk.models.metadata_import_run_progress import MetadataImportRunProgress
from cloudglue.sdk.models.metadata_import_filter_set import MetadataImportFilterSet

# Find Moments (client.find_moments) and moments collections
from cloudglue.sdk.models.find_moments import FindMoments as FindMomentsJob
from cloudglue.sdk.models.find_moments_list import FindMomentsList
from cloudglue.sdk.models.new_find_moments import NewFindMoments
from cloudglue.sdk.models.moment import Moment
from cloudglue.sdk.models.moment_finding import MomentFinding
from cloudglue.sdk.models.moment_criterion import MomentCriterion
from cloudglue.sdk.models.moment_criterion_attachment import MomentCriterionAttachment
from cloudglue.sdk.models.new_moment_criterion_attachment import NewMomentCriterionAttachment
from cloudglue.sdk.models.moments_config import MomentsConfig
from cloudglue.sdk.models.criterion_score import CriterionScore
from cloudglue.sdk.models.moment_search_result import MomentSearchResult
from cloudglue.sdk.models.collection_moments_list import CollectionMomentsList
from cloudglue.sdk.models.collection_moment_findings_list import CollectionMomentFindingsList
from cloudglue.sdk.models.find_moments_find_moments_config import FindMomentsFindMomentsConfig
from cloudglue.sdk.models.moment_criterion_attachment_options import MomentCriterionAttachmentOptions

# Sites (client.sites): per-route unfurl previews
from cloudglue.sdk.models.site_route_preview import SiteRoutePreview
from cloudglue.sdk.models.site_route_preview_input import SiteRoutePreviewInput
from cloudglue.sdk.models.site_route_preview_list import SiteRoutePreviewList

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
    "IconikSourceMetadata",
    "MetadataImport",
    "MetadataImportDetail",
    "MetadataImportList",
    "MetadataImportRun",
    "MetadataImportRunProgress",
    "MetadataImportFilterSet",
    "FindMomentsJob",
    "FindMomentsList",
    "NewFindMoments",
    "Moment",
    "MomentFinding",
    "MomentCriterion",
    "MomentCriterionAttachment",
    "NewMomentCriterionAttachment",
    "MomentsConfig",
    "CriterionScore",
    "MomentSearchResult",
    "CollectionMomentsList",
    "CollectionMomentFindingsList",
    "FindMomentsFindMomentsConfig",
    "MomentCriterionAttachmentOptions",
    "SiteRoutePreview",
    "SiteRoutePreviewInput",
    "SiteRoutePreviewList",
]
