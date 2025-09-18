from tqdm import tqdm
from typing import Optional, Dict
from isahitlab.operations.base import BaseAction
from isahitlab.domain.dataset import DatasetPayload
from isahitlab.api.dataset.api import DatasetApi

from typeguard import typechecked

class CreateDatasetOperation(BaseAction):
    """Create dataset operation"""

    @typechecked
    def run(
        self,
        project_id : str,
        dataset : DatasetPayload,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Create a dataset
        
        Args:
            project_id: ID of the batch
            dataset : See DatasetPayload
            disable_progress_bar: Disable the progress bar display
        """

        dataset_api = DatasetApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Creating dataset... ") as loader:
            created_dataset = dataset_api.create_dataset(project_id=project_id, dataset=dataset)
            loader.update(1)

        return created_dataset
    