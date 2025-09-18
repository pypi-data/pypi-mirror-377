from typing import Dict, Generator, Iterable, List, Optional, Union, cast

from isahitlab.actions.base import BaseAction
from isahitlab.domain.integration import (IntegrationVisibility, IntegrationType, IntegrationFilters, IntegrationPayload)
from isahitlab.operations.integration.get_integrations import GetIntegrationsOperation
from isahitlab.operations.integration.create_integration import CreateIntegrationOperation
from typeguard import typechecked


class IntegrationsActions(BaseAction):
    """Integrations actions"""

    @typechecked
    def integrations(
        self,
        visibility_in: Optional[List[IntegrationVisibility]] = None,
        search: Optional[str] = None,
        disable_progress_bar: Optional[bool] = False,
        iterate: Optional[bool] = False
    ) -> Union[Generator[Iterable[Dict],None,None],Iterable[Dict]] :
        """ Get the list of your integrations and those of your organization
        
        Args:
            visibility_in: Only in those visibilities.
                Possible choices: `organization`, `private`.
            search: Quicksearch,
            disable_progress_bar: Disable the progress bar display,
            iterate: Return a generator

        Returns:
            List (or Generator) of integration representations
        """

        filters = IntegrationFilters(
            visibility_in = cast(List[IntegrationVisibility], visibility_in) if visibility_in else None,
            search = search if search else None,
        )
        
        operation_gen = GetIntegrationsOperation(self.http_client).run(filters=filters, disable_progress_bar=disable_progress_bar)

        if iterate:
            return operation_gen
        else:
            return list(operation_gen)
    

    @typechecked
    def create_integration(
        self,
        name: str,
        type: IntegrationType,
        visibility: IntegrationVisibility,
        bucket_access_point: str,
        role_id: Optional[str] = None,
        external_id: Optional[str] = None,
        disable_progress_bar: Optional[bool] = False
    ) -> Dict:
        """ Create an integration

        Args:
            name: Name of the batch
            type: Type of the integration,
                Possible choices: `GCP`, `S3`.
            visibility: Visibility of the integration
                Possible choices: `organization`, `private`.
            bucket_access_point: Access point for S3 or bucket for GCP
            role_id: Role ID or ARN for S3 integration
            external_id: Client external ID for S3 integration
            disable_progress_bar: Disable the progress bar display

        """

        integration = IntegrationPayload(
            name=name,
            type=type,
            visibility=visibility,
            access_point=bucket_access_point,
            role_id=role_id,
            external_id=external_id
        )

        if integration.type == 'S3' and (not integration.role_id or not integration.external_id):
            raise ValueError('role_id and external_id are mandatory for S3 integration')


        return CreateIntegrationOperation(self.http_client).run(integration=integration, disable_progress_bar=disable_progress_bar)
