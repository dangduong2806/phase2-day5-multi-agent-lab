"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from langsmith import trace


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Span context that logs to local metrics and optionally sends to LangSmith."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}

    is_langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2") == "true"

    if is_langsmith_enabled:
        with trace(
            name=name,
            run_type="chain",
            inputs=attributes or {}
        ) as active_run:
            try:
                yield span
                active_run.end(outputs={"status": "success", "span": span})
            except Exception as e:
                active_run.end(error=str(e))
                raise e
            finally:
                span["duration_seconds"] = perf_counter() - started
    else:
        try:
            yield span
        finally:
            span["duration_seconds"] = perf_counter() - started
