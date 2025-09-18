from typing import Dict, Optional, Union

from isahitlab.actions.base import BaseAction
from isahitlab.domain.batch import (BatchPayload, BatchId)
from isahitlab.domain.dataset import (DatasetId)
from isahitlab.operations.batch.create_batch import CreateBatchOperation
from isahitlab.operations.batch.link_dataset_to_batch import LinkDatasetToBatchOperation
from isahitlab.operations.batch.delete_batch import DeleteBatchOperation
from typeguard import typechecked


class BatchActions(BaseAction):
    """Batches actions"""

    @typechecked
    def create_batch(
        self,
        project_id: str,
        name: str,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Create a batch in a project

        Args:
            project_id: ID of the project
            name: Name of the batch
            disable_progress_bar: Disable the progress bar display

        """

        batch = BatchPayload(name=name)

        return CreateBatchOperation(self.http_client).run(project_id=project_id, batch=batch, disable_progress_bar=disable_progress_bar)

    @typechecked
    def link_dataset_to_batch(
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

        return LinkDatasetToBatchOperation(self.http_client).run(batch_id=batch_id, dataset_id=dataset_id, disable_progress_bar=disable_progress_bar)

    @typechecked
    def delete_batch(
        self,
        batch_id: BatchId,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Delete a batch and all the tasks associated to it

        Args:
            batch_id: ID of the batch
            disable_progress_bar: Disable the progress bar display

        """

        return DeleteBatchOperation(self.http_client).run(batch_id=batch_id, disable_progress_bar=disable_progress_bar)
