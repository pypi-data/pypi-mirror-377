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

logger = logging.getLogger('isahitlab.get_webhook')


class GetWebhook(BaseAction):
    """Create task actions
    """


    _batch_api : BatchApi
    _workflow_api : WorkflowApi

    @typechecked
    def run(
        self,
        project_id: ProjectId,
        batch_id: Optional[BatchId] = None,
        workflow_id: Optional[WorkflowId] = None

    ) -> Dict:
        """ Setup a webhook for a workflow

        !!! warning
            You must provide either a batch_id or a workflow_id
        
        Args:
            project_id: ID of the project
            batch_id: ID of the batch 
            workflow_id: ID of the workflow project
            webhook : See WebhookPayload (url : str, header : str)
            disable_progress_bar: Disable the progress bar display

        """
        self._batch_api = BatchApi(self._http_client)
        self._workflow_api = WorkflowApi(self._http_client)

        if not workflow_id and not batch_id:
            raise ValueError('You must provide either a batch_id or a workflow_id')
        
        if workflow_id:
            return self._workflow_api.get_workflow_by_id(workflow_id=workflow_id)
        elif batch_id:
            batch = self._batch_api.get_batch_by_id(batch_id=batch_id)
            if not batch:
                raise ValueError("Batch not found")
            if batch["projectId"] != project_id:
                raise ValueError("The batch is not part of the project")
            
            workflow_id = batch.get("workflow", {}).get("id")
            if not workflow_id:
                raise Exception("The batch doesn't have a workflow")

            workflow = self._workflow_api.get_workflow_by_id(workflow_id=workflow_id)

            if not workflow:
                raise Exception("Workflow not found")
            
            return workflow.get('webhook', None)