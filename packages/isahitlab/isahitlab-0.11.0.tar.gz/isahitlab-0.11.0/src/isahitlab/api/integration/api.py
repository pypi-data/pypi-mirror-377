from typing import Dict, Generator
import time
from isahitlab.api.base import BaseApi
from isahitlab.domain.integration import IntegrationFilters, IntegrationPayload
from ..helpers import get_response_json, log_raise_for_status, Paginated
from .mappers import integration_filters_mapper

class IntegrationApi(BaseApi):
    """Project API Calls"""

    def get_all_integrations(self, filters: IntegrationFilters) -> Generator[tuple[Dict, int, int], None, None] :
        """Get integrations"""

        page = 1
        limit = 10

        filters.pagination = True
        filters.limit = limit

        while True:
            filters.page = page

            paginated: Paginated = self._get_integration_page(filters)
            docs = paginated['docs']
            page = paginated['nextPage']

            # Count already loaded
            totalDocs = paginated['totalDocs']
            loaded = (paginated['page'] - 1) * paginated['limit'] + len(docs)

            yield (docs, loaded, totalDocs)

            if not paginated['hasNextPage']:
                break

            time.sleep(0.5)



    
    def _get_integration_page(self, filters: IntegrationFilters) -> Paginated :
        """Get integration page"""
        
        tasks = self._http_client.get('api/file-manager/integrations', params=integration_filters_mapper(filters))
        
        log_raise_for_status(tasks)
        
        return get_response_json(tasks)
    

    def create_integration(self, integration: IntegrationPayload):
        """Create batch in a project"""

        data = {
            "name": integration.name,
            "type": integration.type,
            "visibility": integration.visibility,
            "accessPoint" : integration.access_point
        }

        if integration.type == 'S3':
            data['roleId'] = integration.role_id
            data['externalId'] = integration.external_id


        result = self._http_client.post('api/file-manager/integrations', json=data, params={ "preventSharedDuplicate" : "true" })

        log_raise_for_status(result)

        return get_response_json(result)
