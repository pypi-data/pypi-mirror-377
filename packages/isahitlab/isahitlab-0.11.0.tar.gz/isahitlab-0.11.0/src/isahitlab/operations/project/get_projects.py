from tqdm import tqdm
from typing import Optional, Dict, List, Generator
from isahitlab.operations.base import BaseAction
from isahitlab.domain.project import ProjectFilters
from isahitlab.api.project.api import ProjectApi

from typeguard import typechecked

class GetProjectsOperation(BaseAction):
    """Get project actions"""

    @typechecked
    def run(
        self,
        filters: ProjectFilters,
        disable_progress_bar: Optional[bool] = False
    ) -> Generator[List[Dict], None, None]:
        """ Get projects
        
        Args:
            filters : ProjectFilters object
            disable_progress_bar: Disable the progress bar display
        """

        project_api = ProjectApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Loading projects... ") as loader:
             for (docs, loaded, total) in project_api.get_all_projects(filters):
                loader.total = total
                yield from docs
                loader.update(loaded - loader.n)
    