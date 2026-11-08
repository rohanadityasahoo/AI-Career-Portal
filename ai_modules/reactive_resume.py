"""Reactive Resume API integration for polished PDF exports."""

import json
import os

import httpx

REACTIVE_TEMPLATES = {
    "modern": "azurill",
    "minimal": "onyx",
    "classic": "bronzor",
}


def _base_url():
    return os.getenv("REACTIVE_RESUME_API_URL", "https://rxresu.me/api/openapi").rstrip("/")


def _headers():
    key = os.getenv("REACTIVE_RESUME_API_KEY", "").strip()
    return {"x-api-key": key}


def _split_lines(value):
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def _entry_lines(value):
    lines = _split_lines(value)
    if not lines:
        return []
    entries = []
    current = None
    for line in lines:
        if current is None:
            current = {"name": line, "description": []}
        elif line.startswith(("-", "*", "+")):
            current["description"].append(line.lstrip("-*+ "))
        else:
            current["description"].append(line)
    if current:
        entries.append(current)
    return entries


def build_json_resume(draft, template_key="modern"):
    contact = str(draft.get("contact", ""))
    email = next((part.strip() for part in contact.split("|") if "@" in part), "")
    phone = next((part.strip() for part in contact.split("|") if any(ch.isdigit() for ch in part)), "")
    links = [
        part.strip()
        for part in contact.split("|")
        if part.strip().startswith(("http://", "https://"))
    ]
    return {
        "basics": {
            "name": draft.get("name", ""),
            "label": draft.get("headline", ""),
            "email": email,
            "phone": phone,
            "url": links[0] if links else "",
            "summary": draft.get("summary", ""),
        },
        "work": [
            {
                "name": entry["name"],
                "position": "",
                "highlights": entry["description"],
            }
            for entry in _entry_lines(draft.get("experience"))
        ],
        "projects": [
            {
                "name": entry["name"],
                "description": "",
                "highlights": entry["description"],
            }
            for entry in _entry_lines(draft.get("projects"))
        ],
        "education": [{"institution": entry["name"], "studyType": "", "area": "", "summary": "\n".join(entry["description"])} for entry in _entry_lines(draft.get("education"))],
        "skills": [{"name": "Skills", "keywords": _split_lines(draft.get("skills"))}],
        "certificates": [{"name": line} for line in _split_lines(draft.get("certifications"))],
        "metadata": {
            "template": REACTIVE_TEMPLATES.get(
                template_key, REACTIVE_TEMPLATES["modern"]
            )
        },
    }


def export_pdf(draft, template_key="modern"):
    """Import a JSON Resume into Reactive Resume and return exported PDF bytes."""
    if not os.getenv("REACTIVE_RESUME_API_KEY", "").strip():
        return None
    headers = _headers()
    base = _base_url()
    payload = json.dumps(build_json_resume(draft, template_key)).encode("utf-8")
    with httpx.Client(timeout=45, follow_redirects=True) as client:
        imported = client.post(
            f"{base}/resumes/file-imports",
            headers=headers,
            files={"file": ("resume.json", payload, "application/json")},
            data={"format": "JSON_RESUME"},
        )
        imported.raise_for_status()
        body = imported.json()
        resume_id = body if isinstance(body, str) else body.get("id") or body.get("resumeId")
        if not resume_id:
            raise ValueError("Reactive Resume did not return a resume ID.")

        reactive_template = REACTIVE_TEMPLATES.get(
            template_key, REACTIVE_TEMPLATES["modern"]
        )
        patched = client.patch(
            f"{base}/resumes/{resume_id}",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "operations": [
                    {
                        "op": "replace",
                        "path": "/metadata/template",
                        "value": reactive_template,
                    }
                ]
            },
        )
        patched.raise_for_status()

        exported = client.get(f"{base}/resumes/{resume_id}/exports/pdf", headers=headers)
        exported.raise_for_status()
        return exported.content
