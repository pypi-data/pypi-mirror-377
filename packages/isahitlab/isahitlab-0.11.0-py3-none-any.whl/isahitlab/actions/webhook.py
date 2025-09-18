from typing import Dict, Generator, Iterable, List, Optional, Union, cast

from isahitlab.actions.base import BaseAction
from isahitlab.domain.workflow import WebhookPayload
from isahitlab.operations.webhook.get_webhook import GetWebhook
from isahitlab.operations.webhook.setup_webhook import SetupWebhook
from typeguard import typechecked


class WebhookActions(BaseAction):
    """Webhook actions"""

    @typechecked
    def setup_webhook(
        self,
        project_id: str,
        webhook_url: str,
        webhook_header: Optional[str] = None,
        batch_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        disable_progress_bar: Optional[bool] = False
    ) -> None :
        """ Setup a webhook for a workflow

        !!! warning
            If you only set the `project_id` parameter, the webhook will be set on all batches of the project
        
        Args:
            project_id: ID of the project
            webhook_url: URL to call
            webhook_header: Authorization header to set on the webhook requests
            batch_id: ID of the batch 
            workflow_id: ID of the workflow project
            disable_progress_bar: Disable the progress bar display

        Returns:
            None
        """

        webhook_payload : WebhookPayload = WebhookPayload(url=webhook_url, header=webhook_header)
        
        SetupWebhook(self.http_client).run(project_id=project_id, workflow_id=workflow_id, batch_id=batch_id, webhook=webhook_payload, disable_progress_bar=disable_progress_bar)

        print("Webhook setup complete!")

    @typechecked
    def get_webhook(
        self,
        project_id: str,
        batch_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> Dict :
        """ Get a webhook for a workflow

        !!! warning
            You must provide a `batch_id` of a `workflow_id`
        
        Args:
            project_id: ID of the project
            batch_id: ID of the batch 
            workflow_id: ID of the workflow project

        Returns:
            Webhook representation
        """

        if not batch_id and not workflow_id:
            raise ValueError("You must provide a batch ID of a workflow ID")

        
        return GetWebhook(self.http_client).run(project_id=project_id, workflow_id=workflow_id, batch_id=batch_id)