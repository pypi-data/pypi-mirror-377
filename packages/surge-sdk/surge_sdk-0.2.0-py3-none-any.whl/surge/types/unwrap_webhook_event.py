# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from .call_ended_webhook_event import CallEndedWebhookEvent
from .message_sent_webhook_event import MessageSentWebhookEvent
from .message_failed_webhook_event import MessageFailedWebhookEvent
from .message_received_webhook_event import MessageReceivedWebhookEvent
from .campaign_approved_webhook_event import CampaignApprovedWebhookEvent
from .message_delivered_webhook_event import MessageDeliveredWebhookEvent
from .conversation_created_webhook_event import ConversationCreatedWebhookEvent

__all__ = ["UnwrapWebhookEvent"]

UnwrapWebhookEvent: TypeAlias = Union[
    CallEndedWebhookEvent,
    CampaignApprovedWebhookEvent,
    ConversationCreatedWebhookEvent,
    MessageDeliveredWebhookEvent,
    MessageFailedWebhookEvent,
    MessageReceivedWebhookEvent,
    MessageSentWebhookEvent,
]
