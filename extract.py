"""
Structured extraction for job postings.

Implement ``extract(text: str) -> JobPosting`` using OpenAI's structured-output
API: pass ``response_format={"type": "json_schema", "json_schema": {...}}`` with
``strict: True``.

Schema note (READ THIS): OpenAI's ``strict: True`` mode rejects the default
output of ``JobPosting.model_json_schema()`` (every property must appear in
``required``, no ``default`` values, ``additionalProperties: false`` on every
object). Use the ``to_strict_schema`` helper from ``schema.py`` instead. It
walks the pydantic schema and applies the required patches.

Required model: ``gpt-4o-mini``. Do not use a larger model; it costs more and
does not score better on this task. The pedagogical bottleneck is prompt and
schema design, not model size.

Hard requirements (see assignment brief):

1. Read the API key from ``OPENAI_API_KEY``. Never hardcode.
2. Validate every LLM output against the ``JobPosting`` pydantic model.
3. Implement exactly one repair retry: on ``ValidationError``, send the error text
   back to the model and try once more before giving up.
4. Do NOT change the signature below. The final project imports it directly.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from schema import JobPosting, to_strict_schema

load_dotenv()


MODEL = "gpt-4o-mini"


SYSTEM_PROMPT = """\
# TODO (assignment): write your extraction system prompt here.
# Iterate on this prompt. Log each version in iterations.md with its score.
"""


def extract(text: str) -> JobPosting:
    """Extract structured fields from a raw job posting.

    Returns a validated ``JobPosting``. Raises on the second failed attempt.
    """
    # TODO: implement.
    raise NotImplementedError("Implement extract() using response_format=json_schema.")


if __name__ == "__main__":
    raw = sys.stdin.read()
    print(extract(raw).model_dump_json(indent=2))
