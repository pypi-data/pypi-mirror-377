import io
import logging
from typing import Dict, List, Optional

from isahitlab.api.dataset.api import DatasetApi
from isahitlab.domain.batch import BatchId
from isahitlab.domain.dataset import DatasetId, FilePayload
from isahitlab.domain.project import ProjectId
from isahitlab.operations.base import BaseAction
from isahitlab.exceptions import ApiBadRequest
from tqdm import tqdm
from typeguard import typechecked

logger = logging.getLogger('isahitlab.append_to_dataset')


class AppendToDatasetOperation(BaseAction):
    """Upload files to a dataset

    """


    _dataset_api : DatasetApi

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        dataset_id: BatchId,
        files: List[FilePayload],
        ignore_exist_errors: Optional[bool] = False,
        disable_progress_bar: Optional[bool] = False,
    ) -> None:
        """ Add resources to a dataset
        
            project_id: ID of the project
            dataset_id: ID of the dataset_id
                You can also provide a batch_id to use the dataset linked to the batch
            batch_id: ID of the batch
            files : list of the file to create, str or Dict -> FilePayload(path : str, file : str | io.IOBase)
            disable_progress_bar: Disable the progress bar display
        """
        self._dataset_api = DatasetApi(self._http_client)
        nb_files = len(files)
        
        with tqdm(total=nb_files,  disable=disable_progress_bar, desc="Uploading files... ") as loader:
            for file in files:
                try:
                    self._upload_file(file.file, file.path, dataset_id, project_id)
                except ApiBadRequest as err:
                    if ignore_exist_errors and err.errorCode == 4002:
                        pass
                    else:
                        raise
                loader.update(1)
            
    
    def _upload_file(self, resource: str, folder: str, dataset_id: DatasetId, project_id: ProjectId) -> Dict:
        if isinstance(resource, tuple):
            file_info = self._dataset_api.upload_file(dataset_id=dataset_id, project_id=project_id, file=resource, folder=folder)
        else:
            with open(resource, 'rb') as f:
                file_info = self._dataset_api.upload_file(dataset_id=dataset_id, project_id=project_id, file=f, folder=folder)
        return file_info

