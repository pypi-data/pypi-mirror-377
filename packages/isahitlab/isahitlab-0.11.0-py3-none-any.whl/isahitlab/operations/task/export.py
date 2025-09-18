from typing import Any, Dict

from isahitlab.api.project_configuration.api import ProjectConfigurationApi
from isahitlab.api.task.api import TaskApi
from isahitlab.domain.export import ExportFormat
from isahitlab.domain.project import ProjectId
from isahitlab.domain.task import TaskFilters
from isahitlab.formatters import get_export_formatter
from isahitlab.operations.base import BaseAction
from tqdm import tqdm
from typeguard import typechecked


class ExportOperation(BaseAction):
    """Tasks actions"""

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        format: ExportFormat,
        filters: TaskFilters,
        options: Dict = {},
        disable_progress_bar: bool = False
    ) -> Any :
        """ Export tasks
        
        Args:
            project_id: ID of the project
            filters : TaskFilters object
            disable_progress_bar: Disable the progress bar display
            compatibility_mode: Format the output for specific use cases
                Possible choices: `kili` -> format the ouput to look like kili.assets() results 

        """
        project_configuration_api = ProjectConfigurationApi(self._http_client)
        task_api = TaskApi(self._http_client)
       

        # Load configuration and initialize the formatter if required
        with tqdm(total=1,  disable=disable_progress_bar, desc="Loading project configuration... ") as loader:
            project_configuration = project_configuration_api.get_project_configuration(project_id)
            loader.update(1)            

        formatter = get_export_formatter("lab", format, project_configuration, { **options, "extra_filename_part" : project_id  })

        if not formatter:
            raise Exception("No formatter found for {}".format(format))
        
        # load and format task
        with tqdm(total=0,  disable=disable_progress_bar, desc="Loading tasks... ") as loader:
            for (docs, loaded, total) in task_api.get_all_tasks(filters):
                loader.total = total
                for task in docs:
                    formatter.append_task_to_export(task)
                loader.update(loaded - loader.n)

        return formatter.complete_export()
    
