"""Owner-local values shared by domain policy and application ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class CandidateReference:
    candidate_id: str
    manifest_digest: str


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    manifest_digest: str
    bytes_by_path: Mapping[str, bytes]


@dataclass(frozen=True, slots=True)
class Snapshot:
    snapshot_id: str
    candidate: Candidate


@dataclass(frozen=True, slots=True)
class RequestContext:
    context_id: str


@dataclass(frozen=True, slots=True)
class EffectOutcome:
    status: str
    result_digest: str | None = None
