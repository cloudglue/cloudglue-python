# cloudglue/client/resources/sites.py
"""Sites resource for Cloudglue API."""
from typing import Any, Dict, List, Union

from cloudglue.sdk.models.replace_site_route_previews_request import (
    ReplaceSiteRoutePreviewsRequest,
)
from cloudglue.sdk.models.site_route_preview_input import SiteRoutePreviewInput
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class Sites:
    """Per-route unfurl previews for published Cloudglue sites.

    Every page of a published site (e.g. a clip page like ``#/clip/intro``)
    can register its own preview: a card (title, description, image), a hero
    share that the Cloudglue Slack app plays when a link to that page is
    unfurled, and an optional ``startSeconds``/``endSeconds`` clip window so
    the unfurled player plays exactly that clip. Links to routes with no
    registered preview fall back to the site-level preview fields.

    Routes are stored and matched in canonical form: hash-router prefixes
    (``#/``), query strings, and surrounding slashes are stripped, so
    ``/clip/intro``, ``clip/intro/``, and ``#/clip/intro`` all name the same
    route.
    """

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def list_route_previews(self, site_id: str):
        """List the site's per-route unfurl previews, ordered by route.

        Args:
            site_id: The ID of the site.

        Returns:
            SiteRoutePreviewList with the registered previews.

        Raises:
            CloudglueError: If there is an error listing the previews.
        """
        try:
            return self.api.list_site_route_previews(site_id=site_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def replace_route_previews(
        self,
        site_id: str,
        previews: List[Union[SiteRoutePreviewInput, Dict[str, Any]]],
    ):
        """Replace the site's complete set of per-route unfurl previews.

        The set is replaced wholesale — typically written by the same
        pipeline that publishes the site. An empty list clears all route
        previews. Each entry requires ``route`` and ``previewShareId`` (a
        same-account video share; public when the site is public) and may
        carry ``previewTitle``/``previewDescription``/``previewImageUrl``
        card overrides plus a ``startSeconds``/``endSeconds`` clip window
        (both-or-neither, end > start; trimmed at the asset's HLS segment
        boundaries, not frame-accurate).

        Args:
            site_id: The ID of the site.
            previews: The complete set of previews, as
                SiteRoutePreviewInput objects or plain dicts (dict keys may
                be the wire camelCase names or pythonic snake_case).

        Returns:
            SiteRoutePreviewList with the stored previews (canonical routes).

        Raises:
            CloudglueError: If validation fails (duplicate canonical routes,
                empty route, non-video or private-on-public-site heroes, or
                an invalid clip window) or the site is not found.
        """
        try:
            # model_validate (not from_dict) so plain dicts may use either the
            # wire camelCase keys or pythonic snake_case field names.
            normalized = [
                SiteRoutePreviewInput.model_validate(p) if isinstance(p, dict) else p
                for p in previews
            ]
            request = ReplaceSiteRoutePreviewsRequest(previews=normalized)
            return self.api.replace_site_route_previews(
                site_id=site_id,
                replace_site_route_previews_request=request,
            )
        except CloudglueError:
            raise
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete_route_preview(self, site_id: str, preview_id: str):
        """Delete one route preview.

        Links to that route fall back to the site-level preview fields at
        their next unfurl.

        Args:
            site_id: The ID of the site.
            preview_id: The ID of the route preview to delete.

        Returns:
            The deleted SiteRoutePreview.

        Raises:
            CloudglueError: If the site or preview is not found.
        """
        try:
            return self.api.delete_site_route_preview(
                site_id=site_id, preview_id=preview_id
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))
