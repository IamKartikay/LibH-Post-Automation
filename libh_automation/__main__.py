from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from libh_automation.pipeline import run_pipeline


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Library Herald DOCX → Wix draft posts")
    parser.add_argument("--docx", required=True, help="Path to a Library Herald data-entry DOCX")
    parser.add_argument("--out", default="out", help="Output directory")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write payloads without calling Wix (default: true)",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Use the deterministic parser instead of Ollama",
    )
    args = parser.parse_args()
    summary = run_pipeline(
        Path(args.docx),
        out_dir=args.out,
        dry_run=args.dry_run,
        skip_llm=args.skip_llm,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
