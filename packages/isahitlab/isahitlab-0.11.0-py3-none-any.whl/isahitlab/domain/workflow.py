from dataclasses import dataclass
from typing import NewType, Optional

WorkflowId = NewType("WorkflowId", str)

@dataclass
class WebhookPayload:
    """Webhook payload
    
    Args:
        url: URL to call
        header: Authorization header
    """

    url: str
    header: Optional[str] = None
