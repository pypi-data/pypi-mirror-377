"""isahit lab Python SDK client"""

import os
from typing import Optional

from . import log

logger = log.setup_custom_logger('IsahitLab')

from isahitlab.core.http.http_client import Credentials, HttpClient
from isahitlab.exceptions import AuthenticationFailed

from isahitlab.actions.task import TaskActions
from isahitlab.actions.dataset import DatasetActions
from isahitlab.actions.project_configuration import ProjectConfigurationActions
from isahitlab.actions.project import ProjectActions
from isahitlab.actions.webhook import WebhookActions
from isahitlab.actions.batch import BatchActions
from isahitlab.actions.integration import IntegrationsActions



class IsahitLab(
    TaskActions,
    ProjectConfigurationActions,
    DatasetActions,
    ProjectActions,
    WebhookActions,
    IntegrationsActions,
    BatchActions
):
    def __init__(
        self,
        access_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        defer_auth: bool = True,
        http_retry_attempts = 0
    ) -> None:
        """Initialize isahit lab client

        Args:
            access_id: Use ISAHIT_LAB_API_ACCESS_ID environment variable if not provided
            secret_key: Use ISAHIT_LAB_API_SECRET_KEY environment variable if not provided
            endpoint: Use ISAHIT_LAB_API_ENDPOINT environment variable if not provided or the default https://hub-api.isahit.com/ 
        """
        
        endpoint = endpoint or os.getenv(
            "ISAHIT_LAB_API_ENDPOINT",
            "https://hub-api.isahit.com/"
        )
        
        access_id = access_id or os.getenv("ISAHIT_LAB_API_ACCESS_ID")
        secret_key = secret_key or os.getenv("ISAHIT_LAB_API_SECRET_KEY")
        
        if not access_id or not secret_key:
            raise AuthenticationFailed(access_id, secret_key)
        
        credentials: Credentials = {
            "access_id" : access_id,
            "secret_key" : secret_key
        }
        
        self.http_client = HttpClient(
            endpoint=endpoint,
            credentials=credentials,
            defer_auth=defer_auth,
            retry_max_attempts=http_retry_attempts
        )