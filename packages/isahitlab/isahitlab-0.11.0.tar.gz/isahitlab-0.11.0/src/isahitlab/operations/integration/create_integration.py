from tqdm import tqdm
from typing import Optional, Dict
from isahitlab.operations.base import BaseAction
from isahitlab.domain.integration import IntegrationPayload
from isahitlab.api.integration.api import IntegrationApi

from typeguard import typechecked

class CreateIntegrationOperation(BaseAction):
    """Create integration operation"""

    @typechecked
    def run(
        self,
        integration : IntegrationPayload,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Create an integration
        
        Args:
            project_id: ID of the batch
            integration : See IntegrationPayload
            disable_progress_bar: Disable the progress bar display
        """

        integration_api = IntegrationApi(self._http_client)
        with tqdm(total=1,  disable=disable_progress_bar, desc="Creating integration... ") as loader:
            created_integration = integration_api.create_integration(integration=integration)
            loader.update(1)

        return created_integration
    