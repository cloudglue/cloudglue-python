# cloudglue/client/resources/find_moments.py
"""Find Moments resource for Cloudglue API."""
import time
from typing import Any, Dict, List, Optional, Union

from cloudglue.sdk.models.new_find_moments import NewFindMoments
from cloudglue.sdk.models.moment_criterion import MomentCriterion
from cloudglue.sdk.rest import ApiException

from cloudglue.client.resources.base import CloudglueError


class FindMoments:
    """Handles Find Moments: rubric-driven discovery of moments in a video.

    A run takes a source ``url`` and an inline ``criterion`` — a rubric plus
    optional typed output declarations (``moment_schema``,
    ``finding_schema``, ``anchors``, and exactly one ``scoring`` key). The
    criterion is snapshotted and hashed onto the run as ``criterion_hash``.

    Runs reuse a compatible describe or create one internally, so a missing
    describe is never an error; ``describe_job_id`` pins a specific one.

    Every accepted moment is persisted. ``limit``, ``min_score``, and
    ``sort`` are read-time parameters on :meth:`get` — selection never
    destroys accepted results, and ``total_moments`` always reports the full
    accepted count.
    """

    def __init__(self, api):
        """Initialize with the API client."""
        self.api = api

    def create(
        self,
        url: str,
        criterion: Union[MomentCriterion, Dict[str, Any]],
        describe_job_id: Optional[str] = None,
        signals_required: Optional[List[str]] = None,
        boundary_policy: Optional[str] = None,
        speaker_filter: Optional[Dict[str, Any]] = None,
        min_duration_seconds: Optional[float] = None,
        max_duration_seconds: Optional[float] = None,
        cache_policy: Optional[str] = None,
    ):
        """Run exhaustive moment discovery for one criterion over one video.

        Args:
            url: 'cloudglue://files/<id>' or an ingestible URL (same
                resolution rules as describe/extract).
            criterion: The inline rubric (MomentCriterion or dict): ``name``
                and ``instructions`` are required; ``moment_schema``,
                ``finding_schema``, ``anchors``, and ``scoring`` are
                optional typed output declarations.
            describe_job_id: Optional pin to a specific describe. It must
                exist for the file and its config must cover
                ``signals_required``.
            signals_required: Signals the criterion needs from the describe.
            boundary_policy: 'sentence', 'tight', or 'loose'.
            speaker_filter: Restrict discovery to particular speakers.
            min_duration_seconds: Drop moments shorter than this.
            max_duration_seconds: Drop moments longer than this.
            cache_policy: 'reuse' (default behavior) or 'refresh'.

        Returns:
            FindMoments object; poll :meth:`get` until it settles.

        Raises:
            CloudglueError: If there is an error creating the run.
        """
        try:
            request = NewFindMoments(
                url=url,
                criterion=criterion,
                describe_job_id=describe_job_id,
                signals_required=signals_required,
                boundary_policy=boundary_policy,
                speaker_filter=speaker_filter,
                min_duration_seconds=min_duration_seconds,
                max_duration_seconds=max_duration_seconds,
                cache_policy=cache_policy,
            )
            return self.api.create_find_moments(new_find_moments=request)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def list(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        url: Optional[str] = None,
    ):
        """List find-moments runs, newest first, with cursor pagination.

        Pagination is over runs, never over joined moment rows.

        Args:
            limit: Maximum number of runs to return.
            cursor: Opaque cursor from a previous page.
            status: 'pending', 'processing', 'completed', 'failed', or
                'cancelled' (deleting an in-flight run cancels it).
            created_before: Upper bound on creation time.
            created_after: Lower bound on creation time.
            url: Only runs for this source url.

        Returns:
            FindMomentsList object.

        Raises:
            CloudglueError: If there is an error listing runs.
        """
        try:
            return self.api.list_find_moments(
                limit=limit,
                cursor=cursor,
                status=status,
                created_before=created_before,
                created_after=created_after,
                url=url,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def get(
        self,
        job_id: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
        sort: Optional[str] = None,
    ):
        """Get a run; when completed it includes moments and findings.

        The read parameters shape the response only — ``total_moments``
        always reports the full accepted count.

        Args:
            job_id: The ID of the run.
            limit: Maximum moments to return.
            min_score: Drop moments whose criterion score is below this.
            sort: 'rank_score' (API default) or 'start_time'.

        Returns:
            FindMoments object.

        Raises:
            CloudglueError: If there is an error retrieving the run.
        """
        try:
            return self.api.get_find_moments(
                job_id=job_id,
                limit=limit,
                min_score=min_score,
                sort=sort,
            )
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def delete(self, job_id: str):
        """Delete a run along with its moments and findings.

        An in-flight run is cancelled and refunded; a completed run is not
        refunded.

        Args:
            job_id: The ID of the run.

        Returns:
            DeleteFindMomentsResult confirmation.

        Raises:
            CloudglueError: If there is an error deleting the run.
        """
        try:
            return self.api.delete_find_moments(job_id=job_id)
        except ApiException as e:
            raise CloudglueError(str(e), e.status, e.data, e.headers, e.reason)
        except Exception as e:
            raise CloudglueError(str(e))

    def wait_for_ready(
        self,
        job_id: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
        sort: Optional[str] = None,
        polling_interval: float = 5.0,
        max_attempts: int = 60,
    ):
        """Poll a run until it reaches a terminal state.

        Polls :meth:`get` until the run is completed, failed, or cancelled,
        and returns the final FindMoments either way — a failed run is
        returned with its ``error`` message intact so callers can inspect why
        it failed, matching the other wait helpers in this client.

        The attempt cap defaults to 60 rather than the client-wide 36:
        moment discovery reads the whole video and routinely runs past three
        minutes.

        Args:
            job_id: The ID of the run.
            limit: Read-time limit applied to each fetch.
            min_score: Read-time score floor applied to each fetch.
            sort: Read-time sort applied to each fetch.
            polling_interval: Seconds between polls.
            max_attempts: Maximum number of polls before giving up.

        Returns:
            The final FindMoments object (status 'completed', 'failed', or
            'cancelled'; on failure, ``error`` carries the details).

        Raises:
            CloudglueError: If polling itself errors or the timeout is
                reached.
        """
        attempts = 0
        while attempts < max_attempts:
            run = self.get(job_id, limit=limit, min_score=min_score, sort=sort)
            if run.status in ("completed", "failed", "cancelled"):
                return run
            time.sleep(polling_interval)
            attempts += 1

        raise CloudglueError(
            f"Timeout waiting for find-moments run {job_id} after {max_attempts} attempts"
        )
