from typing import NewType, Union, Tuple, Optional, TypedDict, Iterable
import io
from dataclasses import dataclass
from isahitlab.domain.integration import IntegrationId

DatasetId = NewType("DatasetId", str)

@dataclass
class FilePayload(dict):
    """Task payload for task create

    Inherit from dict to make it JSON serializable
    
    Args:
        file: Name of the task (appended to the path, it must be unique in a dataset)
        path: Path of a resource (ex.: "./images/image1.jpg")
    """

    file: Union[str, Tuple[str, io.IOBase]]
    path:  Union[str, None]
    

@dataclass
class DatasetBrowsingFilters:
    """Dataset browsing filters
    Args:
        dataset_id: ID of the dataset to browse
        folder: Path in the dataset
        next_token: Token identifying the next page
    """
    
    dataset_id: str
    folder: Optional[str] = None
    next_token: Optional[str] = None


@dataclass
class DatasetPayload:
    """Dataset payload
    
    Args:
        name: Name of the dataset
        integration_id: ID of the integration to use
        base_folder: path to a folder in the integration bucket
    """

    name: str
    integration_id:  Optional[IntegrationId] = None
    base_folder:  Optional[str] = None



class FileBrowsing(TypedDict):
    """Paginated result"""

    files: Iterable[str]
    folders: Iterable[str]
    nextToken: Union[str, None]
    
