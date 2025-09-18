import logging
from typing import List, Optional

from isahitlab.api.task.api import TaskApi
from isahitlab.domain.task import TaskId
from isahitlab.operations.base import BaseAction
from tqdm import tqdm
from typeguard import typechecked

logger = logging.getLogger('isahitlab.redo_tasks')


class RedoTasksOperation(BaseAction):
    """Send tasks to redo
    """

    _task_api : TaskApi

    @typechecked
    def run(
        self,
        project_id: str,
        task_id_in: List[TaskId],
        reset: Optional[bool] = False,
        disable_progress_bar: Optional[bool] = False,
    ) -> int:
        """ Redo tasks
        
        Args:
            project_id: ID of the project
            task_id_in: List of the IDs of the tasks to redo
            reset: Reset the task data to the initial data
            disable_progress_bar: Disable the progress bar display


        """
        self._task_api = TaskApi(self._http_client)
                
        with tqdm(total=len(task_id_in),  disable=disable_progress_bar, desc="Sending tasks to redo... ") as loader:
            for task_id in task_id_in:
                self._task_api.redo_tasks(project_id=project_id, task_id=task_id, reset=reset )
                loader.update(1)
            

        
        return len(task_id_in)
    