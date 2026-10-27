"""Pure decision logic for the post-repair causal protocol.

This module cannot validate a spacetime, exterior, causal curve, or theorem.
It tests only that downstream status labels do not exceed independently
supplied authorities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TerminalStatus(str, Enum):
    LOCALIZED = "localized"
    NOT_LOCALIZED = "not_localized"
    INCOMPLETE = "incomplete"


class BracketStatus(str, Enum):
    CERTIFIED = "certified"
    NUMERICAL_CANDIDATE = "numerical_candidate"
    ABSENT = "absent"


@dataclass(frozen=True)
class Evidence:
    # True means claim-grade Gate 0B, not merely a one-resolution Gate 0A pilot.
    companion_admitted: bool
    terminal_status: TerminalStatus
    bracket_status: BracketStatus
    certified_bracket_atlas: bool = False
    terminal_front_inside_certified_bracket: bool = False
    heldout_terminal_pass: bool = False
    same_development: bool = True
    same_exterior: bool = True
    finite_wall_used_as_exterior_without_authority: bool = False
    capture_is_only_later_ray_entry: bool = False
    bracket_meets_physical_target: bool = False
    causal_past_equality_authorized: bool = False


def classify(e: Evidence) -> str:
    """Return the strongest allowed outcome from already reviewed evidence."""
    if not e.companion_admitted:
        return "BLOCKED-UNQUALIFIED-COMPANION"

    if e.finite_wall_used_as_exterior_without_authority:
        return "INVALID-EXTERIOR-AUTHORITY"

    bracket = e.bracket_status
    if e.capture_is_only_later_ray_entry and bracket is BracketStatus.CERTIFIED:
        bracket = BracketStatus.NUMERICAL_CANDIDATE

    if bracket is BracketStatus.CERTIFIED and (
        not e.same_development
        or (not e.same_exterior and not e.causal_past_equality_authorized)
    ):
        return "INVALID-CROSS-LINEAGE-OR-EXTERIOR-BRACKET"

    if e.terminal_status is TerminalStatus.INCOMPLETE:
        if bracket is BracketStatus.CERTIFIED:
            return "CERTIFIED-END-RELATIVE-HORIZON-BRACKET__TERMINAL-ESTIMATOR-INCOMPLETE"
        return "TECHNICALLY-INCOMPLETE"

    if bracket is BracketStatus.CERTIFIED:
        if (
            e.certified_bracket_atlas
            and e.terminal_status is TerminalStatus.LOCALIZED
            and e.terminal_front_inside_certified_bracket
            and e.heldout_terminal_pass
            and e.bracket_meets_physical_target
        ):
            return "TERMINAL-FRONT-LOCATOR-SUPPORTED-WITHIN-CERTIFIED-BRACKET-ATLAS"
        if e.terminal_status is TerminalStatus.NOT_LOCALIZED:
            return "CERTIFIED-END-RELATIVE-HORIZON-BRACKET__TERMINAL-ESTIMATOR-NOT-LOCALIZED"
        if not e.certified_bracket_atlas:
            return "CERTIFIED-HORIZON-INTERSECTION-BRACKET__FRONT-IDENTITY-UNRESOLVED"
        return "CERTIFIED-HORIZON-BRACKET-ATLAS__FRONT-IDENTITY-NOT-ESTABLISHED"

    if e.terminal_status is TerminalStatus.LOCALIZED:
        return "REPRESENTED-TERMINAL-LOCALIZATION__CAUSAL-IDENTITY-UNRESOLVED"

    return "NO-CAUSAL-CONCLUSION"
