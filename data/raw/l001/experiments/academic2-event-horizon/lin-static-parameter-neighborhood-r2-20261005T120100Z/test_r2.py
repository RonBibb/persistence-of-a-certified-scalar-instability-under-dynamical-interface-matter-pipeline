#!/usr/bin/env python3
"""Focused R2 recovery-policy tests."""

from __future__ import annotations

import importlib


r2 = importlib.import_module("r2_runner")


def test_nonfinite_conversion_becomes_conservative_obstruction() -> None:
    original = r2._ORIGINAL_EVENT_RECORD
    try:
        def raises(*args, **kwargs):
            raise ValueError("fmpq requires an exact, finite value")
        r2._ORIGINAL_EVENT_RECORD = raises
        row = r2.guarded_event_record(None, None, None, 1, "independent")
        assert row["validated"] is False
        assert row["obstruction"] == "NONFINITE_EVENT_UNION_REQUIRES_SUBDIVISION"
    finally:
        r2._ORIGINAL_EVENT_RECORD = original


def test_unrelated_value_error_remains_fatal() -> None:
    original = r2._ORIGINAL_EVENT_RECORD
    try:
        def raises(*args, **kwargs):
            raise ValueError("different failure")
        r2._ORIGINAL_EVENT_RECORD = raises
        try:
            r2.guarded_event_record(None, None, None, 1, "primary")
        except ValueError as exc:
            assert str(exc) == "different failure"
        else:
            raise AssertionError("unrelated ValueError was swallowed")
    finally:
        r2._ORIGINAL_EVENT_RECORD = original


def test_scientific_configuration_is_r1_plus_policy_only() -> None:
    expected = dict(r2.r1.CONFIG)
    expected["schema"] = r2.CONFIG["schema"]
    expected["nonfinite_event_union_policy"] = r2.CONFIG["nonfinite_event_union_policy"]
    assert r2.CONFIG == expected
