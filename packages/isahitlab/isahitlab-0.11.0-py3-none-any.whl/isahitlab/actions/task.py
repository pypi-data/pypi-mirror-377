import warnings
from typing import Any, Dict, Generator, Iterable, List, Optional, Union, cast

from isahitlab.actions.base import BaseAction
from isahitlab.domain.batch import BatchId
from isahitlab.domain.export import ExportFormat
from isahitlab.domain.project import ProjectFilters, ProjectId, ProjectType
from isahitlab.domain.task import (TaskCompatibilityMode, TaskFilters, TaskId,
                                   TaskOptionalFields, TaskPayload, TaskStatus)
from isahitlab.operations.project.get_projects import GetProjectsOperation
from isahitlab.operations.task.create_tasks import CreateTaskOperation
from isahitlab.operations.task.export import ExportOperation
from isahitlab.operations.task.get_tasks import GetTasksOperation
from isahitlab.operations.task.update_properties import UpdatePropertiesOperation
from isahitlab.operations.task.redo_tasks import RedoTasksOperation
from isahitlab.operations.task.to_review_tasks import ToReviewTasksOperation
from isahitlab.helpers.list import remove_duplicates
from typeguard import typechecked


class TaskActions(BaseAction):
    """Tasks actions"""

    @typechecked
    def tasks(
        self,
        project_id: ProjectId,
        batch_id_in: Optional[List[str]] = None,
        status_in: Optional[List[str]] = None,
        task_id_in: Optional[List[TaskStatus]] = None,
        name_in: Optional[List[str]] = None,
        name_like: Optional[str] = None,
        data: Optional[Dict[str, Union[str, int, float]]] = None,
        properties: Optional[Dict[str, Union[str, int, float]]] = None,
        created_at_gt: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lt: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        updated_at_gt: Optional[str] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lt: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        optional_fields: Optional[List[TaskOptionalFields]] = ["data"],
        disable_progress_bar: Optional[bool] = False,
        compatibility_mode: Optional[TaskCompatibilityMode] = None,
        raw_data: Optional[bool] = False,
        iterate: Optional[bool] = False
    ) -> Union[Generator[Iterable[Dict], None, None], Iterable[Dict]]:
        """ Get a list of tasks

        !!! warning "No data by default"
            Add `"data"` in the `optional_fields` if you want to get your task data

        Args:
            project_id: ID of the project
            batch_id_in: A list of batch ids to filter
            status_in: Only in those statuses.
                Possible choices: `pending`, `complete`, `to-review`, `reviewed`, `configuring`.
            task_id_in: Only task whose ID is in this list,
            name_in: Only task whose name is in this list,
            name_like: Only task whose name mathes this regex,
            data: Dict of data / input filters,
            properties: Dict of property filters,
            created_at_gt: Only tasks created after this date (Ex.: "2022-09-19 08:30:00")
            created_at_gte: Only tasks created at or after this date (Ex.: "2022-09-19 08:30:00")
            created_at_lt: Only tasks created before this date (Ex.: "2022-09-19 08:30:00")
            created_at_lte: Only tasks created at or before this date (Ex.: "2022-09-19 08:30:00")
            updated_at_gt: Only tasks updated after this date (Ex.: "2022-09-19 08:30:00")
            updated_at_gte: Only tasks updated at or after this date (Ex.: "2022-09-19 08:30:00")
            updated_at_lt: Only tasks updated before this date (Ex.: "2022-09-19 08:30:00")
            updated_at_lte: Only tasks updated at or before this date (Ex.: "2022-09-19 08:30:00")
            optional_fields: retreive those additional information
                Possible choices: `data`, `jobs`, `metrics`, `data.mask`(for segmentation project).
            disable_progress_bar: Disable the progress bar display
            compatibility_mode: Format the output for specific use cases
                Possible choices: `kili` -> format the ouput to look like kili.assets() results 
            raw_data: Get raw data and metadata object instead of merged data
            iterate: Return a generator

        Returns:
            List (or Generator) of tasks representations
        """

        filters = TaskFilters(
            project_id=project_id,
            batch_id_in=cast(
                List[BatchId], batch_id_in) if batch_id_in else None,
            status_in=cast(List[TaskStatus], status_in) if status_in else None,
            task_id_in=cast(List[TaskId], task_id_in) if task_id_in else None,
            name_in=cast(List[str], name_in) if name_in else None,
            name_like=name_like if name_like else None,
            created_at_gt=cast(
                List[str], created_at_gt) if created_at_gt else None,
            created_at_gte=cast(
                List[str], created_at_gte) if created_at_gte else None,
            created_at_lt=cast(
                List[str], created_at_lt) if created_at_lt else None,
            created_at_lte=cast(
                List[str], created_at_lte) if created_at_lte else None,
            updated_at_gt=cast(
                List[str], updated_at_gt) if updated_at_gt else None,
            updated_at_gte=cast(
                List[str], updated_at_gte) if updated_at_gte else None,
            updated_at_lt=cast(
                List[str], updated_at_lt) if updated_at_lt else None,
            updated_at_lte=cast(
                List[str], updated_at_lte) if updated_at_lte else None,
            optional_fields=cast(
                List[TaskOptionalFields], optional_fields) if optional_fields else None,
            data=cast(Dict[str, Union[str, int, float]], data) if data else None,
            properties=cast(Dict[str, Union[str, int, float]], properties) if properties else None
        )

        operation = GetTasksOperation(self.http_client)

        operation_gen = operation.run(project_id=project_id, filters=filters,
                                      disable_progress_bar=disable_progress_bar or iterate, compatibility_mode=compatibility_mode, raw_data=raw_data)

        if iterate:
            return operation_gen
        else:
            return list(operation_gen)

    @typechecked
    def create_tasks(
        self,
        project_id: str,
        batch_id: str,
        tasks: List[Dict],
        disable_progress_bar: Optional[bool] = False,
        disable_data_check: Optional[bool] = False,
        disable_unicity_check: Optional[bool] = False,
        raise_if_existing: Optional[bool] = True,
        compatibility_mode: Optional[TaskCompatibilityMode] = None
    ) -> Iterable[Dict]:
        """ Create tasks in a batch

        Args:
            project_id: ID of the project
            batch_id: ID of the batch project
            tasks: List of the tasks to create. See TaskPayload(name: str, resource: str, data: Dict[str, Any], properties: Optional[Dict[str, Any]])
            disable_progress_bar: Disable the progress bar display
            disable_data_check: Set this option to False to ignore the data format validation
            disable_unicity_check: Set this option to True to ignore duplicate check and insert it anyway
            raise_if_existing: Set this option to False to skip task duplicates and only show a warning
            compatibility_mode: Format the output for specific use cases
                Possible choices: `kili` -> format the ouput to look like kili.assets() results 

        """

        projects = list(GetProjectsOperation(self.http_client).run(filters=ProjectFilters(
            id_in=[project_id]), disable_progress_bar=disable_progress_bar))
        project = projects[0] if len(projects) > 0 else None

        if not project:
            warnings.warn('Project not found')
            return

        operation = CreateTaskOperation(self.http_client)
        task_payloads = [*map(lambda t: TaskPayload(
            name=t['name'],
            properties=t.get('properties', None),
            resources=t.get('resources', None),
            data=t['data'] if 'data' in t else None
        ), tasks)]

        tasks = operation.run(project_id=project_id,
                              batch_id=batch_id,
                              tasks=task_payloads,
                              disable_progress_bar=disable_progress_bar,
                              disable_unicity_check=disable_unicity_check,
                              raise_if_existing=raise_if_existing,
                              disable_data_check=disable_data_check,
                              compatibility_mode=compatibility_mode
                              )

        return tasks

    @typechecked
    def update_properties_of_tasks(
        self,
        project_id: str,
        task_id_in: List[str],
        properties: Dict[str, Any],
        disable_progress_bar: Optional[bool] = False
    ) -> int:
        """ Update properties of tasks

        Args:
            project_id: ID of the project
            task_id_in: List of the IDs of the tasks to update
            properties: Dict of properties
                Possible keys : `score`, `custom`
            disable_progress_bar: Disable the progress bar display

        !!! info "Custom properties"
            Some properties like `score` are known by the system. 
            To add custom properties, pass a dictionnary of properties in `properties.custom` (see example below).
    

        !!! Example
            ```python
            from isahitlab.client import IsahitLab

            lab = IsahitLab()

            lab.update_properties_of_tasks(
                        project_id='<project_id>', 
                        task_id_in=['<task_id_1>', '<task_id_2>'],
                        properties={
                            "score": 5,
                            "custom": {
                                "my-property" : "my_value"
                            }
                        }
            )

            ```
        """

        task_id_in = remove_duplicates(task_id_in)

        for property in properties.keys():
            if property not in ["score", "custom"]:
                raise ValueError(f"Unknow property {property}")
            
        return UpdatePropertiesOperation(self.http_client).run(
            project_id=project_id, task_id_in=task_id_in, properties=properties, disable_progress_bar=disable_progress_bar)
       

    @typechecked
    def send_tasks_to_redo(
        self,
        project_id: str,
        task_id_in: List[str],
        reset: Optional[bool] = False,
        disable_progress_bar: Optional[bool] = False
    ) -> int:
        """ Send tasks to redo

        Args:
            project_id: ID of the project
            task_id_in: List of the IDs of the tasks to redo
            reset: Reset the task data to the initial data
            disable_progress_bar: Disable the progress bar display

        """

        task_id_in = remove_duplicates(task_id_in)
            
        return RedoTasksOperation(self.http_client).run(project_id=project_id,
            task_id_in=task_id_in, reset=reset, disable_progress_bar=disable_progress_bar)
       

    @typechecked
    def send_tasks_to_review(
        self,
        project_id: str,
        task_id_in: List[str],
        disable_progress_bar: Optional[bool] = False
    ) -> int:
        """ Send tasks to review

        Args:
            project_id: ID of the project
            task_id_in: List of the IDs of the tasks to review
            disable_progress_bar: Disable the progress bar display

        """

        task_id_in = remove_duplicates(task_id_in)
            
        return ToReviewTasksOperation(self.http_client).run(project_id=project_id,
            task_id_in=task_id_in, disable_progress_bar=disable_progress_bar)
       

    @typechecked
    def export_tasks(
        self,
        project_id: ProjectId,
        format: ExportFormat,
        output_folder: Optional[str] = None,
        output_filename: Optional[str] = None,
        in_memory: Optional[bool] = False,
        options: Optional[Dict] = {},
        batch_id_in: Optional[List[str]] = None,
        status_in: Optional[List[str]] = None,
        task_id_in: Optional[List[str]] = None,
        name_in: Optional[List[str]] = None,
        name_like: Optional[str] = None,
        created_at_gt: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lt: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        updated_at_gt: Optional[str] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lt: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        disable_progress_bar: Optional[bool] = False
    ) -> Any:
        """ Export a list of task

        Args:
            project_id: ID of the project
            format: Export format
                Possible choices: `lab`, `kili`, `yolo`, `mask`
            output_folder: Path to the folder where the export will be saved
            output_filename: name of the export
            in_memory: Return the result instead of saving it on file system
            options: Specific options according to the format (see documentation)
            batch_id_in: A list of batch ids to filter
            status_in: Only in those statuses.
                Possible choices: `pending`, `complete`, `to-review`, `reviewed`, `configuring`.
            task_id_in: Only task whose ID is in this list,
            name_in: Only task whose name is in this list,
            name_like: Only task whose name mathes this regex,
            created_at_gt: Only tasks created after this date (Ex.: "2022-09-19 08:30:00")
            created_at_gte: Only tasks created at or after this date (Ex.: "2022-09-19 08:30:00")
            created_at_lt: Only tasks created before this date (Ex.: "2022-09-19 08:30:00")
            created_at_lte: Only tasks created at or before this date (Ex.: "2022-09-19 08:30:00")
            updated_at_gt: Only tasks updated after this date (Ex.: "2022-09-19 08:30:00")
            updated_at_gte: Only tasks updated at or after this date (Ex.: "2022-09-19 08:30:00")
            updated_at_lt: Only tasks updated before this date (Ex.: "2022-09-19 08:30:00")
            updated_at_lte: Only tasks updated at or before this date (Ex.: "2022-09-19 08:30:00")
            disable_progress_bar: Disable the progress bar display

        """

        filters = TaskFilters(
            project_id=project_id,
            batch_id_in=cast(
                List[BatchId], batch_id_in) if batch_id_in else None,
            status_in=cast(List[TaskStatus], status_in) if status_in else None,
            task_id_in=cast(List[TaskId], task_id_in) if task_id_in else None,
            name_in=cast(List[str], name_in) if name_in else None,
            name_like=name_like if name_like else None,
            created_at_gt=cast(
                List[str], created_at_gt) if created_at_gt else None,
            created_at_gte=cast(
                List[str], created_at_gte) if created_at_gte else None,
            created_at_lt=cast(
                List[str], created_at_lt) if created_at_lt else None,
            created_at_lte=cast(
                List[str], created_at_lte) if created_at_lte else None,
            updated_at_gt=cast(
                List[str], updated_at_gt) if updated_at_gt else None,
            updated_at_gte=cast(
                List[str], updated_at_gte) if updated_at_gte else None,
            updated_at_lt=cast(
                List[str], updated_at_lt) if updated_at_lt else None,
            updated_at_lte=cast(
                List[str], updated_at_lte) if updated_at_lte else None,
            optional_fields=["data", "data.mask", "jobs", "metrics"]
        )

        operation = ExportOperation(self.http_client)

        return operation.run(project_id=project_id, filters=filters, format=format, disable_progress_bar=disable_progress_bar, options={
            **options,
            "output_folder": output_folder,
            "output_filename": output_filename,
            "in_memory": in_memory
        })
