import time
from typing import Dict, Generator, Union

from isahitlab.api.base import BaseApi
from isahitlab.domain.batch import BatchFilters, BatchId, BatchPayload
from isahitlab.domain.dataset import DatasetId
from isahitlab.domain.project import ProjectId

from ..helpers import Paginated, get_response_json, log_raise_for_status
from .mappers import batch_filters_mapper


class BatchApi(BaseApi):
    """Batch API Calls"""

    def get_batch_by_id(self, batch_id: BatchId) -> Dict:
        """Get batch"""

        project_configuration = self._http_client.get(
            'api/task-manager/batches/{}'.format(batch_id))

        log_raise_for_status(project_configuration)

        return get_response_json(project_configuration)

    def get_all_batches(self, filters: BatchFilters) -> Generator[tuple[Dict, int, int], None, None]:
        """Get batches"""

        page = 1
        limit = 10

        filters.pagination = True
        filters.limit = limit

        while True:
            filters.page = page

            paginated: Paginated = self._get_batches_page(filters)
            docs = paginated['docs']
            page = paginated['nextPage']

            # Count already loaded
            totalDocs = paginated['totalDocs']
            loaded = (paginated['page'] - 1) * paginated['limit'] + len(docs)

            yield (docs, loaded, totalDocs)

            if not paginated['hasNextPage']:
                break

            time.sleep(0.5)

    def _get_batches_page(self, filters: BatchFilters) -> Paginated:
        """Get batches page"""

        tasks = self._http_client.get(
            'api/task-manager/batches', params=batch_filters_mapper(filters))

        log_raise_for_status(tasks)

        return get_response_json(tasks)

    def get_batches_by_project_id(self, project_id: ProjectId) -> Dict:
        """Get batches of project"""

        project_configuration = self._http_client.get('api/task-manager/batches', params={
            "projectId": project_id
        })

        log_raise_for_status(project_configuration)

        return get_response_json(project_configuration)


    def create_batch(self, project_id: ProjectId, batch: BatchPayload):
        """Create batch in a project"""

        data = {
            "name": batch.name,
            "projectId": project_id
        }

        result = self._http_client.post('api/task-manager/batches', json=data)

        log_raise_for_status(result)

        return get_response_json(result)
    

    def link_dataset_to_batch(self, batch_id: BatchId, dataset_id : Union[DatasetId,None]):
        """Link (or unlink) a dataset to a batch"""

        data = {
            "batchId": batch_id,
            "datasetId": dataset_id
        }

        result = self._http_client.patch('api/task-manager/batches/{}/dataset'.format(batch_id), json=data)

        log_raise_for_status(result)

        return get_response_json(result)
    

    def delete_batch(self, batch_id: BatchId):
        """Delete a batch and all the tasks associated to it"""

        result = self._http_client.delete('api/task-manager/batches/{}'.format(batch_id))

        log_raise_for_status(result)

        return get_response_json(result)
