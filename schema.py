from __future__ import annotations

import copy
from typing import Any, Optional, Literal

from pydantic import BaseModel


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    is_remote: bool
    experience_level: Literal["entry", "mid", "senior", "unknown"]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[Literal["USD", "EUR", "GBP", "other"]] = None
    required_skills: list[str]
    years_experience_min: Optional[int] = None


def to_strict_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Return a JSON schema compatible with OpenAI's structured-outputs ``strict: True``.

    Pydantic's default ``model_json_schema()`` output is NOT accepted by
    ``response_format={"type":"json_schema", "json_schema":{..., "strict": True}}``
    because OpenAI strict mode requires every property to be in ``required``,
    forbids ``default`` values, and requires ``additionalProperties: false`` on
    every object. This helper walks the schema tree and applies those patches.

    Nullable fields remain as ``anyOf`` unions containing a ``"null"`` branch,
    which OpenAI accepts in strict mode.

    Use this in ``extract.py``:

        from schema import JobPosting, to_strict_schema

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "JobPosting",
                "schema": to_strict_schema(JobPosting),
                "strict": True,
            },
        }
    """
    schema = copy.deepcopy(model.model_json_schema())
    _patch(schema)
    return schema


def _patch(node: Any) -> None:
    if not isinstance(node, dict):
        return
    if node.get("type") == "object" and "properties" in node:
        node["additionalProperties"] = False
        node["required"] = list(node["properties"].keys())
        for prop in node["properties"].values():
            _patch(prop)
    node.pop("default", None)
    for union_key in ("anyOf", "oneOf", "allOf"):
        for sub in node.get(union_key, []):
            _patch(sub)
    if "items" in node:
        _patch(node["items"])
    for defs_key in ("$defs", "definitions"):
        for sub in node.get(defs_key, {}).values():
            _patch(sub)
