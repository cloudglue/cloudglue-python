# cloudglue/client/resources/share.py
"""Share resource for Cloudglue API."""
from typing import Dict, Any, Optional

from cloudglue.sdk.models.create_shareable_asset_request import CreateShareableAssetRequest
from cloudglue.sdk.models.update_shareable_asset_request import UpdateShareableAssetRequest
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Share:
    """Handles shareable asset operations for the Cloudglue API."""

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        file_id: str,
        file_segment_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        visibility: Optional[str] = None,
    ):
        """Create a shareable asset.

        Args:
            file_id: The ID of the file to create a shareable asset for.
            file_segment_id: Optional ID of a file segment to share instead of the whole file.
            title: Optional title for the shareable asset.
            description: Optional description for the shareable asset.
            metadata: Optional metadata for the shareable asset.
            visibility: Optional visibility, either 'public' (default) or 'private'.
                'public' assets are viewable by anyone with the link; 'private' assets are
                restricted to members of the owning account and stream via a signed,
                token-gated playback url. Cannot be changed after creation. A file (or
                file segment) can have at most one active share per visibility.

        Returns:
            ShareableAsset object with the share_url.

        Raises:
            CloudglueError: If there is an error creating the shareable asset.
        """
        try:
            request = CreateShareableAssetRequest(
                file_id=file_id,
                file_segment_id=file_segment_id,
                title=title,
                description=description,
                metadata=metadata,
                visibility=visibility,
            )
            return self.api.create_shareable_asset(create_shareable_asset_request=request)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(self, shareable_asset_id: str):
        """Get a specific shareable asset by ID.

        Args:
            shareable_asset_id: The ID of the shareable asset to retrieve.

        Returns:
            ShareableAsset object.

        Raises:
            CloudglueError: If there is an error retrieving the shareable asset.
        """
        try:
            return self.api.get_shareable_asset(id=shareable_asset_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        file_id: Optional[str] = None,
        file_segment_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        visibility: Optional[str] = None,
    ):
        """List shareable assets with optional filtering.

        Args:
            file_id: Filter by file ID.
            file_segment_id: Filter by file segment ID.
            limit: Maximum number of assets to return.
            offset: Number of assets to skip.
            created_before: Filter by creation date (YYYY-MM-DD format, UTC).
            created_after: Filter by creation date (YYYY-MM-DD format, UTC).
            visibility: Filter by visibility, either 'public' or 'private'. A file can
                have one public and one private share.

        Returns:
            ShareableAssetListResponse object.

        Raises:
            CloudglueError: If there is an error listing shareable assets.
        """
        try:
            return self.api.list_shareable_assets(
                file_id=file_id,
                file_segment_id=file_segment_id,
                limit=limit,
                offset=offset,
                created_before=created_before,
                created_after=created_after,
                visibility=visibility,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def update(
        self,
        shareable_asset_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update a shareable asset.

        Args:
            shareable_asset_id: The ID of the shareable asset to update.
            title: New title for the shareable asset.
            description: New description for the shareable asset.
            metadata: New metadata for the shareable asset.

        Returns:
            Updated ShareableAsset object.

        Raises:
            CloudglueError: If there is an error updating the shareable asset.
        """
        try:
            request = UpdateShareableAssetRequest(
                title=title,
                description=description,
                metadata=metadata,
            )
            return self.api.update_shareable_asset(
                id=shareable_asset_id,
                update_shareable_asset_request=request,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, shareable_asset_id: str):
        """Delete a shareable asset.

        Args:
            shareable_asset_id: The ID of the shareable asset to delete.

        Returns:
            Deletion confirmation.

        Raises:
            CloudglueError: If there is an error deleting the shareable asset.
        """
        try:
            return self.api.delete_shareable_asset(id=shareable_asset_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))
