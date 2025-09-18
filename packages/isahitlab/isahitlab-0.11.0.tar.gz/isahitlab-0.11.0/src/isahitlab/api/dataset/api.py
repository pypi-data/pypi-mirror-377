from typing import BinaryIO, Dict, Generator
import time

from isahitlab.api.base import BaseApi
from isahitlab.domain.dataset import DatasetPayload, DatasetBrowsingFilters, FileBrowsing
from isahitlab.domain.project import ProjectId
from .mappers import dataset_browsing_filters_mapper

from ..helpers import get_response_json, log_raise_for_status


class DatasetApi(BaseApi):
    """Dataset API Calls"""

    def browse_dataset(self, filters: DatasetBrowsingFilters) -> Generator[str, None, None] :
        """Browse files"""

        while True:

            paginated: FileBrowsing = self._browse_dataset_page(filters)
            docs = paginated['files']
            filters.next_token = paginated.get('nextToken', None)
            loaded = len(docs)
            yield (docs, loaded)

            if 'nextToken' not in paginated:
                break

            time.sleep(0.5)
    
    
    def _browse_dataset_page(self, filters: DatasetBrowsingFilters) -> FileBrowsing :
        """Get file keys"""
        
        tasks = self._http_client.get('api/file-manager/datasets/{}/list'.format(filters.dataset_id), params=dataset_browsing_filters_mapper(filters))
        
        log_raise_for_status(tasks)
        
        return get_response_json(tasks)
    

    def upload_file(self, project_id: str, dataset_id: str, file : BinaryIO, folder: str) -> Dict :
        """Upload file to dataset"""
        
        files = {'file': file }

        uploaded = self._http_client.post('api/file-manager/datasets/{}/resources'.format(dataset_id), files=files, params={ "projectId" : project_id }, data={ "path": folder })
        
        log_raise_for_status(uploaded)
        
        return get_response_json(uploaded)
    
    
    def create_dataset(self, project_id : ProjectId, dataset: DatasetPayload):
        """Create a dataset in a project"""

        data = {
            "name": dataset.name,
            "projectId" : project_id
        }

        if dataset.integration_id:
            data['integration'] = dataset.integration_id
            data['key'] = dataset.base_folder


        result = self._http_client.post('api/file-manager/datasets', json=data)

        log_raise_for_status(result)

        return get_response_json(result)
