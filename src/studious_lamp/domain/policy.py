"""Technology-neutral policy vocabulary for owner application use cases."""

from __future__ import annotations

from enum import StrEnum


class Operation(StrEnum):
    ADMIT_CANDIDATE = "admit_candidate"
    ASSIGN_PRODUCT_IDENTITY = "assign_product_identity"
    PUBLISH_PRODUCT_OBJECT = "publish_product_object"
    ADOPT_PRODUCT = "adopt_product"
    UPDATE_PROJECTION = "update_projection"


class AuthorizationDecision(StrEnum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


SUPPORTED_OPERATIONS = frozenset(Operation)


def operation_is_supported(operation: str) -> bool:
    return operation in SUPPORTED_OPERATIONS
