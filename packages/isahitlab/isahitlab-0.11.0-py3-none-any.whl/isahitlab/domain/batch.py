from dataclasses import dataclass
from typing import List, Literal, NewType, Optional

from isahitlab.domain.project import ProjectId

from .pagination import PaginationFilters

BatchId = NewType("BatchId", str)
BatchStatus = Literal["pending", "complete", "configuring"]

@dataclass
class BatchFilters(PaginationFilters):
    """Batch filters for running a batch search."""

    project_id: Optional[ProjectId] = None
    status_in: Optional[List[BatchStatus]] = None
    search: Optional[str] = None

@dataclass
class BatchPayload:
    """Batch payload
    
    Args:
        name: Name of the batch
    """

    name: str
