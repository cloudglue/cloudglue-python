# cloudglue/client/resources/__init__.py
"""Cloudglue client resource classes."""

from cloudglue.client.resources.base import CloudglueError
from cloudglue.client.resources.chat import Chat, Completions
from cloudglue.client.resources.collections import Collections
from cloudglue.client.resources.extract import Extract
from cloudglue.client.resources.transcribe import Transcribe
from cloudglue.client.resources.describe import Describe
from cloudglue.client.resources.files import Files
from cloudglue.client.resources.segmentations import Segmentations
from cloudglue.client.resources.segments import Segments
from cloudglue.client.resources.search import Search
from cloudglue.client.resources.thumbnails import Thumbnails
from cloudglue.client.resources.frames import Frames
from cloudglue.client.resources.face_detection import FaceDetection
from cloudglue.client.resources.face_match import FaceMatch
from cloudglue.client.resources.tags import Tags
from cloudglue.client.resources.file_segments import FileSegments
from cloudglue.client.resources.responses import Responses
from cloudglue.client.resources.share import Share
from cloudglue.client.resources.data_connectors import DataConnectors
from cloudglue.client.resources.deep_search import DeepSearch

__all__ = [
    "CloudglueError",
    "Chat",
    "Completions",
    "Collections",
    "Extract",
    "Transcribe",
    "Describe",
    "Files",
    "Segmentations",
    "Segments",
    "Search",
    "Thumbnails",
    "Frames",
    "FaceDetection",
    "FaceMatch",
    "Tags",
    "FileSegments",
    "Responses",
    "Share",
    "DataConnectors",
    "DeepSearch",
]

