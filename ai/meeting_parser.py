import json
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from .models import MeetingDraft

load_dotenv()

MAX_TRANSCRIPT_LENGTH = 50_000

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set")


SYSTEM_PROMPT = """
You are an AI project manager assistant.

Your job is to read a meeting transcript and convert it into
structured project and task information.

Rules:

1. Extract only information supported by the transcript.
2. Never invent a project, client, person, deadline, or estimate.
3. If a required value cannot be determined, use null.
4. Put missing or ambiguous required information in unresolved_fields.
5. A project has:
   - name
   - client
   - description
   - manager_id
   - deadline
   - tasks
6. A task has:
   - title
   - description
   - assignee_id
   - deadline
   - estimated_hours
7. Do not create database IDs.
8. Do not save anything.
9. Do not claim that anything has been saved.
10. Prefer explicit final decisions in the meeting over earlier suggestions.
11. Return only data matching the supplied JSON schema.
"""


def validate_transcript(transcript: str) -> str:
    if not isinstance(transcript, str):
        raise TypeError("Transcript must be a string.")

    transcript = transcript.strip()

    if not transcript:
        raise ValueError("Transcript cannot be empty.")

    if len(transcript) > MAX_TRANSCRIPT_LENGTH:
        raise ValueError(
            f"Transcript is too long. Maximum is "
            f"{MAX_TRANSCRIPT_LENGTH} characters."
        )

    return transcript


def generate_draft(transcript: str) -> MeetingDraft:
    transcript = validate_transcript(transcript)

    with OpenRouter(api_key=OPENROUTER_API_KEY) as client:
        response = client.chat.send(
            model="openrouter/auto",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": transcript,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meeting_project_draft",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "projects": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": ["string", "null"]},
                                        "client": {"type": ["string", "null"]},
                                        "description": {"type": ["string", "null"]},
                                        "manager_id": {"type": ["string", "null"]},
                                        "deadline": {"type": ["string", "null"]},
                                        "tasks": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {
                                                        "type": ["string", "null"]
                                                    },
                                                    "description": {
                                                        "type": ["string", "null"]
                                                    },
                                                    "assignee_id": {
                                                        "type": ["string", "null"]
                                                    },
                                                    "deadline": {
                                                        "type": ["string", "null"]
                                                    },
                                                    "estimated_hours": {
                                                        "type": ["number", "null"]
                                                    },
                                                },
                                                "required": [
                                                    "title",
                                                    "description",
                                                    "assignee_id",
                                                    "deadline",
                                                    "estimated_hours",
                                                ],
                                                "additionalProperties": False,
                                            },
                                        },
                                    },
                                    "required": [
                                        "name",
                                        "client",
                                        "description",
                                        "manager_id",
                                        "deadline",
                                        "tasks",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                            "unresolved_fields": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "project_index": {"type": "integer"},
                                        "task_index": {"type": ["integer", "null"]},
                                        "field": {"type": "string"},
                                        "reason": {"type": "string"},
                                    },
                                    "required": [
                                        "project_index",
                                        "task_index",
                                        "field",
                                        "reason",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                        },
                        "required": [
                            "projects",
                            "unresolved_fields",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
        )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("OpenRouter returned an empty response.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenRouter returned invalid JSON.") from exc

    return MeetingDraft.model_validate(data)
