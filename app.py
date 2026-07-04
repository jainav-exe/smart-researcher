"""CLI entry point for Smart Researcher."""

from __future__ import annotations

import sys

from research_crew import DEFAULT_TOPIC, missing_env_vars, run_research


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    missing = missing_env_vars()
    if missing:
        print("Missing required environment variables:", file=sys.stderr)
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        print(
            "\nAdd them to your .env file or export them in your shell, then retry.",
            file=sys.stderr,
        )
        print(
            "\n  GEMINI_API_KEY  → https://aistudio.google.com/apikey (free)",
            file=sys.stderr,
        )
        print(
            "  SERPER_API_KEY  → https://serper.dev (free tier available)",
            file=sys.stderr,
        )
        sys.exit(1)

    topic = DEFAULT_TOPIC

    print("\n" + "=" * 72)
    print("  SMART RESEARCHER")
    print("=" * 72)
    print(f"  Topic: {topic}")
    print("  LLM:   Gemini 2.5 Flash (free)")
    print("=" * 72 + "\n")

    report = run_research(topic, verbose=True)

    print("\n" + "=" * 72)
    print("  FINAL REPORT")
    print("=" * 72 + "\n")
    print(report)
    print("\n" + "=" * 72)
    print("  Done.")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
