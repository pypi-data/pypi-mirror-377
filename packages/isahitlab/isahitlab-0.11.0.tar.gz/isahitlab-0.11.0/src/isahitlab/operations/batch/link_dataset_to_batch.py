from tqdm import tqdm
from typing import Optional, Dict, Union
from isahitlab.operations.base import BaseAction
from isahitlab.domain.batch import BatchId
from isahitlab.domain.dataset import DatasetId
from isahitlab.api.batch.api import BatchApi

from typeguard import typechecked

class LinkDatasetToBatchOperation(BaseAction):
    """Link (or unlink) a dataset to a batch operation"""

    @typechecked
    def run(
        self,
        batch_id: BatchId,
        dataset_id : Union[DatasetId, None],
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Link (or unlink) a dataset to a batch
        
        Args:
            batch_id: ID of the batch
            dataset_id : ID of the dataset to link or None to unlink a dataset from the batch
            disable_progress_bar: Disable the progress bar display
        """

        batch_api = BatchApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Updating batch... ") as loader:
            updated_batch = batch_api.link_dataset_to_batch(batch_id=batch_id, dataset_id=dataset_id)
            loader.update(1)

        return updated_batch
    