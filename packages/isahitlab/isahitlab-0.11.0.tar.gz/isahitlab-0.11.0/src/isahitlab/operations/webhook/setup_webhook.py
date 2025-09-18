import logging
from typing import Dict, Iterable, Optional

from isahitlab.api.batch.api import BatchApi
from isahitlab.api.workflow.api import WorkflowApi
from isahitlab.domain.batch import BatchFilters, BatchId
from isahitlab.domain.project import ProjectId
from isahitlab.domain.workflow import WebhookPayload, WorkflowId
from isahitlab.operations.base import BaseAction
from tqdm import tqdm
from typeguard import typechecked

logger = logging.getLogger('isahitlab.setup_webhook')


class SetupWebhook(BaseAction):
    """Create task actions
    """


    _batch_api : BatchApi
    _workflow_api : WorkflowApi

    @typechecked
    def run(
        self,
        webhook: WebhookPayload,
        project_id: Optional[ProjectId] = None,
        batch_id: Optional[BatchId] = None,
        workflow_id: Optional[WorkflowId] = None,
        disable_progress_bar: Optional[bool] = False

    ) -> None:
        """ Setup a webhook for a workflow

        !!! warning
            If you only set the project_id parameter, the webhook will be set on all batches of the project
        
        Args:
            project_id: ID of the project
            batch_id: ID of the batch 
            workflow_id: ID of the workflow project
            webhook : See WebhookPayload (url : str, header : str)
            disable_progress_bar: Disable the progress bar display

        """
        self._batch_api = BatchApi(self._http_client)
        self._workflow_api = WorkflowApi(self._http_client)

        if not project_id and not workflow_id and not batch_id:
            raise ValueError('You must provide either a project_id, a batch_id or a workflow_id')
        
        if workflow_id:
            self._workflow_api.setup_webhook_by_workflow_id(workflow_id=workflow_id, webhook=webhook)
        elif batch_id:
            self._workflow_api.setup_webhook_by_batch_id(batch_id=batch_id, webhook=webhook)
        elif project_id:
            # load batches and apply
            filters : BatchFilters = BatchFilters(project_id=project_id)
            with tqdm(total=0,  disable=disable_progress_bar, desc="Setting up the webhook... ") as loader:
                for (docs, loaded, total) in self._batch_api.get_all_batches(filters):
                    loader.total = total
                    for batch in docs:
                        batch_id = batch['_id']
                        self._workflow_api.setup_webhook_by_batch_id(batch_id=batch_id, webhook=webhook)
                    loader.update(loaded - loader.n)
            