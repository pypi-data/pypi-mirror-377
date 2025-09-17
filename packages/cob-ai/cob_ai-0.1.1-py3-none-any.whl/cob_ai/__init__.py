"""COB AI - Python client for COB SharePoint search."""

from .client import COB
from .models import SearchResponse, SearchResult, SyncCompletionStatus, SyncStatusResponse

__version__ = "0.1.0"
__all__ = ["COB", "SearchResponse", "SearchResult", "SyncCompletionStatus", "SyncStatusResponse"]