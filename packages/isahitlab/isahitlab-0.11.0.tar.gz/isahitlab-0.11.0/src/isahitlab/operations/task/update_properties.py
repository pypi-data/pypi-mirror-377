import logging
from typing import List, Optional, Dict, Any

from isahitlab.api.task.api import TaskApi
from isahitlab.domain.project import ProjectId
from isahitlab.domain.task import TaskId
from isahitlab.operations.base import BaseAction
from isahitlab.helpers.list import divide_chunks
from tqdm import tqdm
from typeguard import typechecked

logger = logging.getLogger('isahitlab.update_properties')


class UpdatePropertiesOperation(BaseAction):
    """Update properties of tasks
    """

    _task_api : TaskApi

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        task_id_in: List[TaskId],
        properties: Dict[str, Any],
        disable_progress_bar: Optional[bool] = False,
    ) -> int:
        """ Update tasks properties
        
        Args:
            project_id: ID of the project
            task_id_in: List of the IDs of the tasks to update
            properties; Dict of properties
                Possible keys : `score`
            disable_progress_bar: Disable the progress bar display

        """
        self._task_api = TaskApi(self._http_client)
        
        chunks = divide_chunks(task_id_in, 200)
        updated = 0
        
        with tqdm(total=len(task_id_in),  disable=disable_progress_bar, desc="Updating tasks properties... ") as loader:
            for task_ids in chunks:
                result = self._task_api.update_properties(project_id=project_id, task_ids=task_ids, properties=properties)
                updated += result["updated"]
                loader.update(len(task_ids))
            

        
        return updated
    