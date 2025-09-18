import json
import time
from typing import Dict, Generator, List, Optional, Union

from isahitlab.api.base import BaseApi
from isahitlab.domain.batch import BatchId
from isahitlab.domain.workflow import WebhookPayload, WorkflowId

from ..helpers import get_response_json, log_raise_for_status


class WorkflowApi(BaseApi):
    """Task API Calls"""

    def get_workflow_by_id(self, workflow_id: WorkflowId) -> Dict :
        """Get webhook of workflow"""

        result = self._http_client.get(f'api/workflow-manager/workflows/{workflow_id}')
        
        log_raise_for_status(result)

        return get_response_json(result)
    

    def setup_webhook_by_workflow_id(self, workflow_id : WorkflowId, webhook : WebhookPayload):
        """Setup webhook of workflow"""

        data = {
            "url" : webhook.url,
            "header": webhook.header
        }

        result = self._http_client.patch('api/workflow-manager/workflows/setup-webhook', params={ "workflowId" : workflow_id }, json=data)
        
        log_raise_for_status(result)
    
    def setup_webhook_by_batch_id(self, batch_id : BatchId, webhook : WebhookPayload):
        """Setup webhook of batch"""

        data = {
            "url" : webhook.url,
            "header": webhook.header
        }

        result = self._http_client.patch('api/workflow-manager/workflows/setup-webhook', params={ "batchId" : batch_id }, json=data)
        
        log_raise_for_status(result)

    