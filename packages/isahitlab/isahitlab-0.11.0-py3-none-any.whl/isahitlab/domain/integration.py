"""Integration domain"""

from typing import NewType, Optional, List, Literal
from .pagination import PaginationFilters
from dataclasses import dataclass

IntegrationId = NewType("IntegrationId", str)

IntegrationVisibility = Literal["organization", "private"]
IntegrationType = Literal["GCP", "S3"]


@dataclass
class IntegrationFilters(PaginationFilters):
    """Integration filters."""
    visibility_in: Optional[List[IntegrationVisibility]] = None
    search: Optional[str] = None


@dataclass
class IntegrationPayload:
    """Integration payload
    
    Args:
        name: Name of the batch
        type: Type of the integration,
        visibility: Visibility of the integration
        access_point: Access point (or bucket for GCP)
        role_id: Role ID or ARN for S3 integration
        external_id: Client external ID for S3 integration
    """

    name: str
    type: IntegrationType
    visibility: IntegrationVisibility
    access_point: str
    role_id: Optional[str]
    external_id: Optional[str]
