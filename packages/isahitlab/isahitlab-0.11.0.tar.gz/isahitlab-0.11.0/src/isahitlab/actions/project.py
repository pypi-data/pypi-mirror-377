from typing import Dict, Generator, Iterable, List, Optional, Union, cast

from isahitlab.actions.base import BaseAction
from isahitlab.domain.project import (ProjectFilters, ProjectId, ProjectStatus,
                                      ProjectType)
from isahitlab.operations.project.get_projects import GetProjectsOperation
from typeguard import typechecked


class ProjectActions(BaseAction):
    """Projects actions"""

    @typechecked
    def projects(
        self,
        id_in: Optional[List[str]] = None,
        status_in: Optional[List[str]] = None,
        type_in: Optional[List[str]] = None,
        search: Optional[str] = None,
        disable_progress_bar: Optional[bool] = False,
        iterate: Optional[bool] = False
    ) -> Union[Generator[Iterable[Dict],None,None],Iterable[Dict]] :
        """ Get a projects list
        
        Args:
            id_in: ID of the projects
            status_in: Only in those statuses.
                Possible choices: `configuring`, `pending`, `complete`, `toBeDeleted`, `deleted`, `archived`.
            type_in: Only in those statuses.
                Possible choices:  `form`, `iat-rectangle`, `iat-polygon`, `iat-segmentation`, `iat-graph`, `iat-polyline`
            search: Quicksearch,
            disable_progress_bar: Disable the progress bar display,
            iterate: Return a generator

        Returns:
            List (or Generator) of project representations
        """

        filters = ProjectFilters(
            id_in=cast(List[ProjectId], id_in) if id_in else None, 
            status_in = cast(List[ProjectStatus], status_in) if status_in else None,
            type_in= cast(List[ProjectType], type_in) if type_in else None,
            search = search if search else None,
        )
        
        operation_gen = GetProjectsOperation(self.http_client).run(filters=filters, disable_progress_bar=disable_progress_bar)

        if iterate:
            return operation_gen
        else:
            return list(operation_gen)
    