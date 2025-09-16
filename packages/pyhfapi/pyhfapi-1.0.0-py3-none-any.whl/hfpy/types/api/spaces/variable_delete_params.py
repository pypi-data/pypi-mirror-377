# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VariableDeleteParams"]


class VariableDeleteParams(TypedDict, total=False):
    namespace: Required[str]

    key: Required[str]
