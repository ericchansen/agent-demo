"""CLI entry point for testing the orchestrator locally."""

from __future__ import annotations

import sys

from src.orchestrator.foundry_agent import run_query

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Ask: ")
    print(run_query(question))
