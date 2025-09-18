from typing import Generator, Dict, List, Union, Optional, Any
import time
from isahitlab.api.base import BaseApi
from isahitlab.domain.task import TaskFilters, TaskId
from isahitlab.domain.batch import BatchId
from isahitlab.domain.project import ProjectId
from isahitlab.helpers.list import divide_chunks
from .mappers import task_filters_mapper
from ..helpers import get_response_json, log_raise_for_status, Paginated

class TaskApi(BaseApi):
    """Task API Calls"""

    def get_all_tasks(self, filters: TaskFilters) -> Generator[tuple[Dict, int, int], None, None] :
        """Get tasks"""

        page = 1
        limit = 100

        filters.pagination = True
        filters.limit = limit

        while True:
            filters.page = page

            paginated: Paginated = self._get_tasks_page(filters)
            docs = paginated['docs']
            page = paginated['nextPage']

            # Count already loaded
            totalDocs = paginated['totalDocs']
            loaded = (paginated['page'] - 1) * paginated['limit'] + len(docs)

            yield (docs, loaded, totalDocs)

            if not paginated['hasNextPage']:
                break

            time.sleep(0.5)

    def get_existing_task_names(self, batch_id : BatchId, names: List[str]) -> Dict[str, List[str]]:
        """Get existing task names by chunk"""
        chunks = divide_chunks(names, 500)

        duplicates = []

        for chunk in chunks:
            res = self._get_existing_task_names_chunk(batch_id, chunk)
            if len(res["duplicate"]) > 0:
                duplicates = duplicates + res["duplicate"]

        return duplicates


    def create_task(self, batch_id : BatchId, name : str, resources : List[Union[str, Dict]], data_id : Union[Dict, None], properties: Optional[Dict[str,Any]] = None, grant_resources: Optional[str] = None, grant_data: Optional[str] = None) -> Dict:
        """Create task"""
        
        data = { 
            "name": name,
            "resources" : resources,
            "properties" : properties,
            "dataId" : data_id,
            "grantResources": grant_resources,
            "grantData": grant_data,
        }
        
        created = self._http_client.post('api/task-manager/batches/{}/tasks'.format(batch_id), json=data)

        log_raise_for_status(created)

        return get_response_json(created)
    
    
    def update_properties(self, project_id : ProjectId, task_ids: List[str], properties: Dict[str, Any]) -> Dict[str,int]:
        """Create task"""

        data = { 
            "taskIds": task_ids,
            **properties
        }
        
        created = self._http_client.patch('api/task-manager/projects/{}/tasks/properties'.format(project_id), json=data)

        log_raise_for_status(created)

        return get_response_json(created)
    
    
    def redo_tasks(self, project_id: ProjectId, task_id: TaskId, reset: bool = False) -> Dict[str,int]:
        """Redo task"""

        created = self._http_client.patch('api/task-manager/tasks/{}/reset'.format(task_id), params={ 'projectId': project_id, 'keepState' : 'false' if reset else 'true'})

        log_raise_for_status(created)

        return get_response_json(created)
    
    
    def to_review_tasks(self, project_id: ProjectId, task_id: TaskId) -> Dict[str,int]:
        """Send task to review"""

        created = self._http_client.patch('api/task-manager/tasks/{}/to-review'.format(task_id), params={ 'projectId': project_id})

        log_raise_for_status(created)

        return get_response_json(created)
    
    
    def _get_existing_task_names_chunk(self, batch_id : BatchId, names: List[str]) -> Dict[str, List[str]]:
        """Get existing tasks
        
            Args:
                names: List of name to check (limited to 500)
           """

        existings = self._http_client.patch('api/task-manager/batches/{}/tasks-duplicate'.format(batch_id), json={ "names" : names })

        log_raise_for_status(existings)

        return get_response_json(existings)

    
    def _get_tasks_page(self, filters: TaskFilters) -> Paginated :
        """Get tasks page"""
        
        tasks = self._http_client.get('api/task-manager/tasks', params=task_filters_mapper(filters))
        
        log_raise_for_status(tasks)
        
        return get_response_json(tasks)
    