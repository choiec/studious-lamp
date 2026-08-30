"""Technology-neutral application boundaries implemented by outer adapters."""

from __future__ import annotations

from typing import Protocol

from studious_lamp.domain.models import (
    Candidate,
    CandidateReference,
    EffectOutcome,
    RequestContext,
    Snapshot,
)
from studious_lamp.domain.policy import AuthorizationDecision, Operation


class CandidateIntakePort(Protocol):
    def read_candidate(self, reference: CandidateReference) -> Candidate: ...


class SnapshotCustodyPort(Protocol):
    def retain(self, candidate: Candidate) -> Snapshot: ...

    def read_back(self, snapshot_id: str) -> Snapshot: ...


class CanonicalPublicationPort(Protocol):
    def publish(self, snapshot: Snapshot, idempotency_key: str) -> EffectOutcome: ...


class ProductStatePort(Protocol):
    def record(
        self,
        snapshot: Snapshot,
        operation: Operation,
        idempotency_key: str,
    ) -> EffectOutcome: ...


class DeliveryAuthenticationPort(Protocol):
    def authenticate(self, request: object) -> RequestContext: ...

    def authorize(
        self,
        context: RequestContext,
        operation: Operation,
    ) -> AuthorizationDecision: ...
