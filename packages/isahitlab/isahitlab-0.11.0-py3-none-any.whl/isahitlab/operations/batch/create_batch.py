from tqdm import tqdm
from typing import Optional, Dict
from isahitlab.operations.base import BaseAction
from isahitlab.domain.batch import BatchId, BatchPayload
from isahitlab.domain.project import ProjectId
from isahitlab.api.batch.api import BatchApi

from typeguard import typechecked

class CreateBatchOperation(BaseAction):
    """Create batch operation"""

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        batch : BatchPayload,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Create a batch in a project
        
        Args:
            project_id: ID of the batch
            batch : See BatchPayload (name : str)
            disable_progress_bar: Disable the progress bar display
        """

        batch_api = BatchApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Creating batch... ") as loader:
            created_batch = batch_api.create_batch(project_id=project_id, batch=batch)
            loader.update(1)

        return created_batch
    