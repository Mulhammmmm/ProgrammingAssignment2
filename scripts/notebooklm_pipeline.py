#!/usr/bin/env python3
"""NotebookLM pipeline: create notebooks, add YouTube sources, generate deliverables."""

import argparse
import asyncio
import json
import sys

from notebooklm import NotebookLMClient


def _client(profile: str | None = None):
    return NotebookLMClient.from_storage(profile=profile)


async def create_notebook(name: str, profile: str | None = None) -> dict:
    async with _client(profile) as client:
        nb = await client.notebooks.create(name)
        return {"id": nb.id, "name": name}


async def add_sources(notebook_id: str, urls: list[str], profile: str | None = None) -> list[dict]:
    results = []
    async with _client(profile) as client:
        for url in urls:
            try:
                await client.sources.add_url(notebook_id, url, wait=True)
                results.append({"url": url, "status": "added"})
                print(f"  Added: {url}", flush=True)
            except Exception as exc:
                results.append({"url": url, "status": "error", "error": str(exc)})
                print(f"  Error adding {url}: {exc}", file=sys.stderr, flush=True)
    return results


async def ask_question(notebook_id: str, question: str, profile: str | None = None) -> str:
    async with _client(profile) as client:
        result = await client.chat.ask(notebook_id, question)
        return result.answer


async def generate_artifact(
    notebook_id: str, artifact_type: str, profile: str | None = None, **kwargs
) -> dict:
    async with _client(profile) as client:
        artifacts = client.artifacts
        generators = {
            "audio": artifacts.generate_audio,
            "infographic": artifacts.generate_infographic,
            "slide-deck": artifacts.generate_slide_deck,
            "flashcards": artifacts.generate_flashcards,
            "quiz": artifacts.generate_quiz,
            "mind-map": artifacts.generate_mind_map,
            "video": artifacts.generate_video,
        }
        if artifact_type not in generators:
            raise ValueError(f"Unknown artifact type: {artifact_type}. Choose from: {list(generators)}")

        status = await generators[artifact_type](notebook_id, **kwargs)
        task_id = getattr(status, "task_id", None)
        if task_id:
            await artifacts.wait_for_completion(notebook_id, task_id)
        return {"artifact_type": artifact_type, "status": "complete", "task_id": task_id}


async def list_notebooks(profile: str | None = None) -> list[dict]:
    async with _client(profile) as client:
        notebooks = await client.notebooks.list()
        return [{"id": nb.id, "name": getattr(nb, "name", str(nb.id))} for nb in notebooks]


def add_profile_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        default=None,
        help="notebooklm profile name (run `notebooklm profile list` to see available profiles)",
    )


def main():
    parser = argparse.ArgumentParser(description="NotebookLM pipeline operations")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new notebook")
    p_create.add_argument("name", help="Notebook name")
    add_profile_arg(p_create)

    p_add = sub.add_parser("add-sources", help="Add YouTube URLs as sources")
    p_add.add_argument("notebook_id", help="Notebook ID")
    p_add.add_argument("urls", nargs="+", help="YouTube URLs to add")
    add_profile_arg(p_add)

    p_ask = sub.add_parser("ask", help="Ask a question to the notebook")
    p_ask.add_argument("notebook_id", help="Notebook ID")
    p_ask.add_argument("question", help="Question to ask")
    add_profile_arg(p_ask)

    p_gen = sub.add_parser("generate", help="Generate an artifact")
    p_gen.add_argument("notebook_id", help="Notebook ID")
    p_gen.add_argument(
        "artifact_type",
        choices=["audio", "infographic", "slide-deck", "flashcards", "quiz", "mind-map", "video"],
    )
    p_gen.add_argument("--instructions", default=None, help="Style/instructions for generation")
    p_gen.add_argument("--orientation", choices=["portrait", "landscape"], default=None)
    add_profile_arg(p_gen)

    p_list = sub.add_parser("list", help="List all notebooks")
    add_profile_arg(p_list)

    args = parser.parse_args()
    profile = getattr(args, "profile", None)

    if args.command == "create":
        result = asyncio.run(create_notebook(args.name, profile))
        print(json.dumps(result, indent=2))

    elif args.command == "add-sources":
        result = asyncio.run(add_sources(args.notebook_id, args.urls, profile))
        print(json.dumps(result, indent=2))

    elif args.command == "ask":
        answer = asyncio.run(ask_question(args.notebook_id, args.question, profile))
        print(answer)

    elif args.command == "generate":
        kwargs = {}
        if args.instructions:
            kwargs["instructions"] = args.instructions
        if args.orientation:
            kwargs["orientation"] = args.orientation
        result = asyncio.run(generate_artifact(args.notebook_id, args.artifact_type, profile, **kwargs))
        print(json.dumps(result, indent=2))

    elif args.command == "list":
        result = asyncio.run(list_notebooks(profile))
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
