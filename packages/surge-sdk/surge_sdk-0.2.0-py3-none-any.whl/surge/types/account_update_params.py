# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from .organization_params import OrganizationParams

__all__ = ["AccountUpdateParams"]


class AccountUpdateParams(TypedDict, total=False):
    brand_name: str
    """The name by which the people this account communicates with know it.

    If not provided, this will match the name field.
    """

    name: str
    """
    The name of the account that will be visible for your internal organizational
    purposes. This will also be the default public-facing brand name unless you also
    set a `brand_name`, but otherwise the account name will never be displayed
    anywhere outside of Surge HQ, and may include your ID for the account or
    anything else that may help you.
    """

    organization: OrganizationParams
    """
    Parameters describing the legal entity on whose behalf the account will be
    operated.
    """

    time_zone: Optional[str]
    """The time zone for the account"""
