# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .organization_params import OrganizationParams

__all__ = ["AccountCreateParams"]


class AccountCreateParams(TypedDict, total=False):
    name: Required[str]
    """
    The name of the account that will be visible for your internal organizational
    purposes. This will also be the default public-facing brand name unless you also
    set a `brand_name`, but otherwise the account name will never be displayed
    anywhere outside of Surge HQ, and may include your ID for the account or
    anything else that may help you.
    """

    brand_name: Optional[str]
    """The name by which the people this account communicates with know it.

    If not provided, this will match the name field.
    """

    organization: OrganizationParams
    """
    Parameters describing the legal entity on whose behalf the account will be
    operated.
    """

    time_zone: str
    """This is the time zone in which the account is headquartered.

    This time zone may be used for compliance with TCPA restrictions on when
    messages may be sent.
    """
