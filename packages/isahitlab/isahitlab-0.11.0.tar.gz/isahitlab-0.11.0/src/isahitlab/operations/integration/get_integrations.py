from tqdm import tqdm
from typing import Optional, Dict, List, Generator
from isahitlab.operations.base import BaseAction
from isahitlab.domain.integration import (IntegrationFilters)
from isahitlab.api.integration.api import IntegrationApi

from typeguard import typechecked

class GetIntegrationsOperation(BaseAction):
    """Get integrations actions"""

    @typechecked
    def run(
        self,
        filters: IntegrationFilters,
        disable_progress_bar: Optional[bool] = False
    ) -> Generator[List[Dict], None, None]:
        """ Get the your integrations
        
        Args:
            filters : IntegrationVisibility object
            disable_progress_bar: Disable the progress bar display
        """

        integration_api = IntegrationApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Loading integrations... ") as loader:
             for (docs, loaded, total) in integration_api.get_all_integrations(filters):
                loader.total = total
                yield from docs
                loader.update(loaded - loader.n)
    