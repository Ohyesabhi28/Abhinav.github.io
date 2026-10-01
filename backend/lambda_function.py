"""
Portfolio chat backend: AWS Lambda (Function URL) -> Amazon Bedrock (Converse API).

Request:  POST  {"messages": [{"role": "user" | "assistant", "content": "..."}]}
Response: 200   {"reply": "..."}

CORS is configured on the Function URL itself (see README.md), so this
handler only returns plain JSON.
"""
import json
import os
from pathlib import Path

import boto3

MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
MAX_TURNS = 8          # most recent messages kept
MAX_CHARS = 500        # per message
MAX_OUTPUT_TOKENS = 300

SYSTEM_PROMPT = (Path(__file__).parent / "resume_context.txt").read_text(encoding="utf-8")
bedrock = boto3.client("bedrock-runtime")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _clean_messages(raw):
    """Keep only well-formed user/assistant turns, trimmed, starting with a user turn."""
    cleaned = []
    for m in raw[-MAX_TURNS:]:
        if not isinstance(m, dict):
            continue
        role, content = m.get("role"), m.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str) or not content.strip():
            continue
        # Converse requires alternating roles; drop consecutive same-role turns.
        if cleaned and cleaned[-1]["role"] == role:
            continue
        cleaned.append({"role": role, "content": [{"text": content.strip()[:MAX_CHARS]}]})
    while cleaned and cleaned[0]["role"] != "user":
        cleaned.pop(0)
    if not cleaned or cleaned[-1]["role"] != "user":
        return []
    return cleaned


def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON"})

    messages = payload.get("messages")
    if not isinstance(messages, list):
        return _response(400, {"error": "'messages' must be a list"})

    cleaned = _clean_messages(messages)
    if not cleaned:
        return _response(400, {"error": "No valid user message"})

    try:
        result = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=cleaned,
            inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS, "temperature": 0.4},
        )
        reply = result["output"]["message"]["content"][0]["text"]
    except Exception as exc:  # noqa: BLE001 - surface a generic error to the browser
        print("Bedrock error:", repr(exc))
        return _response(502, {"error": "Model unavailable"})

    return _response(200, {"reply": reply})
