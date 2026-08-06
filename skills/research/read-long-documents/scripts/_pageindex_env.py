"""Shared setup for read-long-documents scripts: locate the PageIndex repo,
put it on sys.path, and fix the two environment blockers that only matter
when an LLM call is about to be made (node summaries during indexing).

Read-only retrieval (list/meta/structure/pages) never calls an LLM, so it
only needs sys.path resolution — see resolve_repo().
"""
import os
import sys
from pathlib import Path

DEFAULT_REPO = "~/code/playground/PageIndex"


def resolve_repo() -> Path:
    """Find the PageIndex repo and add it to sys.path. Does not touch env vars."""
    repo = Path(os.environ.get("PAGEINDEX_REPO", DEFAULT_REPO)).expanduser()
    if not repo.is_dir() or not (repo / "pageindex").is_dir():
        sys.exit(
            f"PageIndex repo not found at {repo}.\n"
            f"Ask the user for the actual path and set PAGEINDEX_REPO to it."
        )
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo


def setup_llm_env(repo: Path) -> None:
    """Fix the env blockers that break LLM calls (needed only before indexing
    with summaries). Never trust ambient OPENAI_API_KEY — it may shadow the
    key PageIndex's own .env sets."""
    from dotenv import load_dotenv

    load_dotenv(repo / ".env", override=True)
    if os.environ.get("OPENAI_API_BASE") and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.environ["OPENAI_API_BASE"]


def default_workspace() -> Path:
    return Path(os.environ.get("PAGEINDEX_WORKSPACE", "~/.pageindex/workspace")).expanduser()
