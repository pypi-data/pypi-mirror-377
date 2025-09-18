from typing import Dict, Generator, Iterable, Optional

from isahitlab.api.project_configuration.api import ProjectConfigurationApi
from isahitlab.api.task.api import TaskApi
from isahitlab.domain.project import ProjectId
from isahitlab.domain.task import TaskCompatibilityMode, TaskFilters
from isahitlab.formatters import get_compatibility_formatter
from isahitlab.operations.base import BaseAction
from tqdm import tqdm
from typeguard import typechecked


class GetTasksOperation(BaseAction):
    """Tasks actions"""

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        filters: TaskFilters,
        disable_progress_bar: Optional[bool] = False,
        raw_data: Optional[bool] = False,
        compatibility_mode: Optional[TaskCompatibilityMode] = None
    ) -> Generator[Iterable[Dict],None,None]:
        """ Get a tasks list generator
        
        Args:
            project_id: ID of the project
            filters : TaskFilters object
            disable_progress_bar: Disable the progress bar display
            raw_data: Get raw data and metadata object instead of merged data
            compatibility_mode: Format the output for specific use cases
                Possible choices: `kili` -> format the ouput to look like kili.assets() results 

        """
        task_api = TaskApi(self._http_client)

        # Load configuration and initialize the formatter if required
        compatibility_mode = compatibility_mode or ("lab" if not raw_data else None)

        formatter = None
        if compatibility_mode:
            project_configuration_api = ProjectConfigurationApi(self._http_client)
            with tqdm(total=1,  disable=disable_progress_bar, desc="Loading project configuration... ") as loader:
                project_configuration = project_configuration_api.get_project_configuration(project_id)
                loader.update(1)            
            formatter = get_compatibility_formatter("lab", compatibility_mode, project_configuration)

        # load and format task
        with tqdm(total=0,  disable=disable_progress_bar, desc="Loading tasks... ") as loader:
            for (docs, loaded, total) in task_api.get_all_tasks(filters):
                loader.total = total
                if formatter :
                    docs = formatter.format_tasks(docs)
                
                yield from docs
                loader.update(loaded - loader.n)

    
