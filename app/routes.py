from numbers import Real
from time import monotonic, sleep

import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


def _json_object():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify(error="The request body must be a JSON object."), 400)
    return payload, None


def _finite_values(payload: dict, field: str, *, minimum: int = 1):
    raw_values = payload.get(field)
    if not isinstance(raw_values, list) or len(raw_values) < minimum:
        message = f"'{field}' must be an array containing at least {minimum} number(s)."
        return None, (jsonify(error=message), 400)

    if any(isinstance(value, bool) or not isinstance(value, Real) for value in raw_values):
        return None, (jsonify(error=f"'{field}' must contain numbers only."), 400)

    values = np.asarray(raw_values, dtype=np.float64)
    if not np.isfinite(values).all():
        return None, (jsonify(error=f"'{field}' must contain finite numbers only."), 400)

    return values, None


@api.get("/")
def index():
    return jsonify(
        name="Flask Data API",
        endpoints=[
            "GET /health",
            "POST /api/v1/summary",
            "POST /api/v1/normalize",
            "POST /api/v1/correlation",
        ],
    )


@api.get("/health")
def health():
    return jsonify(status="ok")


@api.get("/canary/wait/<int:seconds>")
def duration_canary(seconds: int):
    """Bounded launch fixture for validating APIZIT's public duration ceilings."""

    if seconds < 1 or seconds > 130:
        return jsonify(error="'seconds' must be between 1 and 130."), 400

    started_at = monotonic()
    sleep(seconds)
    return jsonify(
        requested_seconds=seconds,
        elapsed_seconds=round(monotonic() - started_at, 3),
        status="completed",
    )


@api.post("/api/v1/summary")
def summary():
    payload, error = _json_object()
    if error:
        return error

    values, error = _finite_values(payload, "values")
    if error:
        return error

    series = pd.Series(values)
    return jsonify(
        count=int(series.count()),
        max=float(series.max()),
        mean=float(series.mean()),
        median=float(series.median()),
        min=float(series.min()),
        percentile_25=float(series.quantile(0.25)),
        percentile_75=float(series.quantile(0.75)),
        population_std_dev=float(np.std(values)),
        sum=float(series.sum()),
    )


@api.post("/api/v1/normalize")
def normalize():
    payload, error = _json_object()
    if error:
        return error

    values, error = _finite_values(payload, "values")
    if error:
        return error

    mean = float(np.mean(values))
    standard_deviation = float(np.std(values))
    normalized = (
        np.zeros_like(values)
        if standard_deviation == 0.0
        else (values - mean) / standard_deviation
    )

    return jsonify(
        mean=mean,
        population_std_dev=standard_deviation,
        values=normalized.tolist(),
    )


@api.post("/api/v1/correlation")
def correlation():
    payload, error = _json_object()
    if error:
        return error

    x_values, error = _finite_values(payload, "x", minimum=2)
    if error:
        return error
    y_values, error = _finite_values(payload, "y", minimum=2)
    if error:
        return error

    if len(x_values) != len(y_values):
        return jsonify(error="'x' and 'y' must contain the same number of values."), 400
    if np.std(x_values) == 0.0 or np.std(y_values) == 0.0:
        return jsonify(error="Correlation is undefined for a constant series."), 422

    coefficient = float(np.corrcoef(x_values, y_values)[0, 1])
    return jsonify(coefficient=coefficient, sample_size=len(x_values))
