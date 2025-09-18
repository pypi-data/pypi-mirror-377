from tqdm import tqdm
from typing import Optional, Dict
from isahitlab.operations.base import BaseAction
from isahitlab.domain.batch import BatchId
from isahitlab.domain.dataset import DatasetId
from isahitlab.api.batch.api import BatchApi

from typeguard import typechecked

class DeleteBatchOperation(BaseAction):
    """Delete a batch operation"""

    @typechecked
    def run(
        self,
        batch_id: BatchId,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Delete a batch and all the tasks associated to it
        
        Args:
            batch_id: ID of the batch
            disable_progress_bar: Disable the progress bar display
        """

        batch_api = BatchApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Deleting batch... ") as loader:
            updated_batch = batch_api.delete_batch(batch_id=batch_id)
            loader.update(1)

        return updated_batch
    