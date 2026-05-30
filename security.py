"""Shared security helpers for the Flask API."""

import os
from functools import wraps
from typing import Callable

from flask import request, jsonify


def api_key_configured() -> bool:
    return bool(os.environ.get("CLAIMS_API_KEY", "").strip())


def require_api_key(view: Callable):
    """Require X-API-Key when CLAIMS_API_KEY is set in the environment."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = os.environ.get("CLAIMS_API_KEY", "").strip()
        if not expected:
            return view(*args, **kwargs)
        provided = request.headers.get("X-API-Key", "")
        if provided != expected:
            return jsonify({"error": "Unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped
