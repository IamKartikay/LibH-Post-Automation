from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

CREATE_DRAFT_URL = "https://www.wixapis.com/blog/v3/draft-posts"
LIST_MEMBERS_URL = "https://www.wixapis.com/members/v1/members"


class WixConfigError(RuntimeError):
    pass


def load_wix_config() -> dict[str, str]:
    api_key = os.getenv("WIX_API_KEY", "").strip()
    site_id = os.getenv("WIX_SITE_ID", "").strip()
    member_id = os.getenv("WIX_MEMBER_ID", "").strip()
    missing = [
        name
        for name, value in (
            ("WIX_API_KEY", api_key),
            ("WIX_SITE_ID", site_id),
            ("WIX_MEMBER_ID", member_id),
        )
        if not value
    ]
    if missing:
        raise WixConfigError(f"Missing environment variables: {', '.join(missing)}")
    return {"api_key": api_key, "site_id": site_id, "member_id": member_id}


def wix_headers(api_key: str, site_id: str) -> dict[str, str]:
    return {
        "Authorization": api_key,
        "wix-site-id": site_id,
        "Content-Type": "application/json",
    }


def list_members(*, api_key: str, site_id: str, timeout: float = 30.0) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        response = client.get(
            LIST_MEMBERS_URL,
            headers=wix_headers(api_key, site_id),
            params={"fieldsets": "PUBLIC", "paging.limit": 1},
        )
        response.raise_for_status()
        return response.json()


def create_draft_post(
    payload: dict[str, Any],
    *,
    api_key: str,
    site_id: str,
    timeout: float = 60.0,
) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            CREATE_DRAFT_URL,
            headers=wix_headers(api_key, site_id),
            json=payload,
        )
        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text}
        if response.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"Wix create draft failed: {response.status_code} {body}",
                request=response.request,
                response=response,
            )
        return body


def write_payload(payload: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
