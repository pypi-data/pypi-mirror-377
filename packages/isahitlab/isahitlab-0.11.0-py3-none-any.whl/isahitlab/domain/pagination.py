"""Task domain"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PaginationFilters:
    """Pagination filters."""

    pagination: bool = True
    page: Optional[int] = 1
    limit: Optional[int] = 10
