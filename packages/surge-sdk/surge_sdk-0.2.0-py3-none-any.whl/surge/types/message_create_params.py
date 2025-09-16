# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .contact_params import ContactParams
from .attachment_params import AttachmentParams

__all__ = [
    "MessageCreateParams",
    "MessageParamsWithConversation",
    "MessageParamsWithConversationConversation",
    "SimpleMessageParams",
]


class MessageParamsWithConversation(TypedDict, total=False):
    conversation: Required[MessageParamsWithConversationConversation]
    """Params for selecting or creating a new conversation.

    Either the id or the Contact must be given.
    """

    attachments: Iterable[AttachmentParams]

    body: str
    """The message body."""

    send_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """
    An optional datetime for scheduling message up to a couple of months in the
    future.
    """


class MessageParamsWithConversationConversation(TypedDict, total=False):
    contact: Required[ContactParams]
    """Parameters for creating a contact"""

    phone_number: str
    """The phone number from which to send the message.

    This can be either the phone number in E.164 format or a Surge phone number id.
    """


class SimpleMessageParams(TypedDict, total=False):
    to: Required[str]
    """The recipient's phone number in E.164 format.

    Cannot be used together with 'conversation'.
    """

    attachments: Iterable[AttachmentParams]

    body: str
    """The message body."""

    from_: Annotated[str, PropertyInfo(alias="from")]
    """The sender's phone number in E.164 format or phone number ID.

    If omitted, uses the account's default phone number. Cannot be used together
    with 'conversation'.
    """

    send_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """
    An optional datetime for scheduling message up to a couple of months in the
    future.
    """


MessageCreateParams: TypeAlias = Union[MessageParamsWithConversation, SimpleMessageParams]
