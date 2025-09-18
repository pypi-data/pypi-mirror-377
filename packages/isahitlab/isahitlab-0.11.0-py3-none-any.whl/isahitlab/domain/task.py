from dataclasses import dataclass
from typing import Any, Dict, List, Literal, NewType, Optional, Union

from .batch import BatchId
from .pagination import PaginationFilters
from .project import ProjectId

TaskId = NewType("TaskId", str)


TaskStatus = Literal["pending", "complete",
                     "to-review", "reviewed", "configuring"]
TaskOptionalFields = Literal["metrics", "jobs", "data", "data.mask"]
TaskCompatibilityMode = Literal["kili", "lab"]


@dataclass
class TaskPayload(dict):
    """Task payload for task creation


    Args:
        name: Name of the task (should be unique in a batch)
        resources: Path or URL of a resource (ex.: "./images/image1.jpg", "https:://domain.com/image1.jpg")
        data: Initial data for the task (depends on project type and configuration)
        properties: See `update_properties_of_tasks(...)`
    """
    # Inherit from dict to make it JSON serializable

    name: str
    data: Dict[str, Any]
    resources: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None

    def __init__(self, name: str, resources: Optional[List[str]], data:  Dict[str, Any], properties: Optional[Dict[str, Any]]):
        self.name = name
        self.resources = resources
        self.data = data
        self.properties = properties
        dict.__init__(self, name=name, resources=resources, data=data)


@dataclass
class TaskFilters(PaginationFilters):
    """Task filters for running a task search."""

    batch_id_in: Optional[List[BatchId]] = None
    project_id: Optional[ProjectId] = None
    status_in: Optional[List[TaskStatus]] = None
    task_id_in: Optional[List[TaskId]] = None
    name_in: Optional[List[str]] = None
    name_like: Optional[str] = None
    created_at_gt: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lt: Optional[str] = None
    created_at_lte: Optional[str] = None
    updated_at_gt: Optional[str] = None
    updated_at_gte: Optional[str] = None
    updated_at_lt: Optional[str] = None
    updated_at_lte: Optional[str] = None
    optional_fields: Optional[List[TaskOptionalFields]] = None
    data: Optional[Dict[str, Union[str, int, float]]] = None
    properties: Optional[Dict[str, Union[str, int, float]]] = None
