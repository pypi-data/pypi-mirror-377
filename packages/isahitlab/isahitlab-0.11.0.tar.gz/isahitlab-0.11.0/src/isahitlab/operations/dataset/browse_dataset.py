from tqdm import tqdm
from typing import Optional, Generator
from isahitlab.operations.base import BaseAction
from isahitlab.domain.dataset import DatasetBrowsingFilters
from isahitlab.api.dataset.api import DatasetApi

from typeguard import typechecked

class BrowseDatasetOperation(BaseAction):
    """Browse dataset operation"""

    @typechecked
    def run(
        self,
        filters : DatasetBrowsingFilters,
        disable_progress_bar: Optional[bool] = False
    ) -> Generator[tuple[str, int, int], None, None]:
        """ Browse a dataset
        
        Args:
            dataset_id: ID of the dataset
            folder : Base folder to start browsing
            disable_progress_bar: Disable the progress bar display
        """

        dataset_api = DatasetApi(self._http_client)
        with tqdm(total=0,  disable=disable_progress_bar, desc="Browsing dataset... ") as loader:            
            for (docs, loaded) in dataset_api.browse_dataset(filters=filters):
                loader.total += loaded                
                yield from docs
                loader.update(loaded)
    