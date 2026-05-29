#!/usr/bin/env python3
"""
End-to-end pipeline: search YouTube → create NotebookLM notebook →
add sources → get analysis → generate infographic.

Usage:
    python3 scripts/pipeline.py "your topic" [--count 25] [--profile default]
    python3 scripts/pipeline.py "your topic" --skip-search --urls url1 url2 ...
"""

import argparse
import asyncio
import json
import sys
import time

import yt_dlp
from notebooklm import NotebookLMClient


# ── YouTube search ────────────────────────────────────────────────────────────

def search_youtube(query: str, count: int) -> list[dict]:
    print(f"\n[1/4] Searching YouTube for: \"{query}\" ({count} videos)…")
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": count,
        "nocheckcertificate": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)

    results = []
    for entry in info.get("entries", []) or []:
        if not entry:
            continue
        vid_id = entry.get("id", "")
        if not vid_id:
            continue
        dur = entry.get("duration")
        if dur:
            m, s = divmod(int(dur), 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        else:
            dur_str = "N/A"
        views = entry.get("view_count")
        results.append({
            "rank": len(results) + 1,
            "title": entry.get("title", "N/A"),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "channel": entry.get("channel") or entry.get("uploader", "N/A"),
            "views": f"{views:,}" if views else "N/A",
            "duration": dur_str,
        })

    print(f"    Found {len(results)} videos.")
    for r in results:
        print(f"    {r['rank']:>2}. {r['title'][:70]}")
    return results


# ── NotebookLM operations ─────────────────────────────────────────────────────

async def run_pipeline(
    topic: str,
    videos: list[dict],
    profile: str | None,
    infographic_style: str,
) -> None:
    notebook_name = f"{topic} — Research {time.strftime('%Y-%m-%d')}"

    async with NotebookLMClient.from_storage(profile=profile) as client:

        # Create notebook
        print(f"\n[2/4] Creating NotebookLM notebook: \"{notebook_name}\"…")
        nb = await client.notebooks.create(notebook_name)
        print(f"    Notebook ID: {nb.id}")

        # Add sources
        print(f"\n[3/4] Adding {len(videos)} YouTube sources…")
        added, failed = 0, 0
        for v in videos:
            try:
                await client.sources.add_url(nb.id, v["url"], wait=True)
                print(f"    ✓ {v['rank']:>2}. {v['title'][:60]}")
                added += 1
            except Exception as e:
                print(f"    ✗ {v['rank']:>2}. {v['title'][:50]} — {e}", file=sys.stderr)
                failed += 1
        print(f"    Sources added: {added}  Failed: {failed}")

        if added == 0:
            print("\nNo sources were added successfully. Aborting.", file=sys.stderr)
            return

        # Ask for analysis
        print("\n[4/4] Requesting analysis from NotebookLM…")
        question = (
            f"Based on all the YouTube videos about '{topic}', what are the top findings, "
            "key trends, and most important insights? Summarise the common themes and "
            "any surprising or noteworthy patterns."
        )
        result = await client.chat.ask(nb.id, question)
        analysis = result.answer
        print("\n" + "═" * 70)
        print("ANALYSIS")
        print("═" * 70)
        print(analysis)
        print("═" * 70)

        # Generate infographic
        print(f"\n[5/5] Generating infographic ({infographic_style})…")
        print("    This may take a minute — NotebookLM is rendering your infographic.")
        status = await client.artifacts.generate_infographic(
            nb.id, instructions=infographic_style, orientation="portrait"
        )
        task_id = getattr(status, "task_id", None)
        if task_id:
            await client.artifacts.wait_for_completion(nb.id, task_id)

        print("\n✅  Done! Your infographic is ready in NotebookLM.")
        print(f"    Open: https://notebooklm.google.com")
        print(f"    Notebook: \"{notebook_name}\"")
        print(f"    Notebook ID: {nb.id}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube → NotebookLM end-to-end pipeline"
    )
    parser.add_argument("topic", help="Research topic (e.g. 'blockchain trends 2025')")
    parser.add_argument("-n", "--count", type=int, default=25,
                        help="Number of YouTube videos (default: 25)")
    parser.add_argument("--profile", default=None,
                        help="notebooklm profile (default: active profile)")
    parser.add_argument("--style", default="handwritten chalkboard style",
                        help="Infographic style instructions")
    parser.add_argument("--skip-search", action="store_true",
                        help="Skip YouTube search and provide URLs manually")
    parser.add_argument("--urls", nargs="+", default=[],
                        help="YouTube URLs to use (with --skip-search)")
    args = parser.parse_args()

    if args.skip_search:
        if not args.urls:
            print("Error: --skip-search requires --urls", file=sys.stderr)
            sys.exit(1)
        videos = [{"rank": i+1, "title": u, "url": u}
                  for i, u in enumerate(args.urls)]
        print(f"Using {len(videos)} provided URLs.")
    else:
        videos = search_youtube(args.topic, args.count)
        if not videos:
            print("No videos found. Try a different query.", file=sys.stderr)
            sys.exit(1)

    asyncio.run(run_pipeline(args.topic, videos, args.profile, args.style))


if __name__ == "__main__":
    main()
