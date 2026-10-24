from __future__ import annotations

import json
from pathlib import Path

from libh_automation.extract import extract_chunks
from libh_automation.llm import process_chunks
from libh_automation.skeleton import merge_skeleton
from libh_automation.validate import foo, write_review_log
from libh_automation.wix import WixConfigError, create_draft_post, load_wix_config, write_payload


def run_pipeline(
    docx_path: str | Path,
    *,
    out_dir: str | Path = "out",
    dry_run: bool = True,
    skip_llm: bool = False,
) -> dict:
    docx_path = Path(docx_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = extract_chunks(docx_path)
    llm_items = process_chunks(chunks, skip_llm=skip_llm)
    (out_dir / "llm_items.json").write_text(
        json.dumps(llm_items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    result = foo(llm_items)
    write_review_log(result, out_dir / "review_log.json")

    member_id = ""
    config = None
    if not dry_run:
        config = load_wix_config()
        member_id = config["member_id"]
    else:
        try:
            member_id = load_wix_config()["member_id"]
        except WixConfigError:
            member_id = "00000000-0000-0000-0000-000000000000"

    posted: list[dict] = []
    payloads: list[dict] = []
    for index, article in enumerate(result.accepted):
        payload = merge_skeleton(article, member_id)
        payloads.append(payload)
        slug = f"{index:02d}_{article.doi.replace('/', '_')}"
        write_payload(payload, out_dir / "payloads" / f"{slug}.json")
        if dry_run:
            posted.append({"dry_run": True, "title": article.title, "file": slug})
            continue
        response = create_draft_post(
            payload,
            api_key=config["api_key"],
            site_id=config["site_id"],
        )
        posted.append({"title": article.title, "response": response})

    summary = {
        "docx": str(docx_path),
        "chunks": len(chunks),
        "accepted": len(result.accepted),
        "needs_review": len(result.needs_review),
        "rejected": len(result.rejected),
        "invalid": len(result.invalid),
        "dry_run": dry_run,
        "posted": posted,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary
