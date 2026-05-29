#!/usr/bin/env python3
"""YouTube research tool using yt-dlp. Scrapes metadata for a search query."""

import argparse
import json
import sys

import yt_dlp


def search_youtube(query: str, max_results: int = 25) -> list[dict]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": max_results,
        "nocheckcertificate": True,
    }

    search_url = f"ytsearch{max_results}:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)

    results = []
    for entry in info.get("entries", []):
        if not entry:
            continue
        duration_s = entry.get("duration")
        if duration_s:
            mins, secs = divmod(int(duration_s), 60)
            hrs, mins = divmod(mins, 60)
            duration_str = f"{hrs}:{mins:02d}:{secs:02d}" if hrs else f"{mins}:{secs:02d}"
        else:
            duration_str = "N/A"

        views = entry.get("view_count")
        views_str = f"{views:,}" if views else "N/A"

        results.append(
            {
                "rank": len(results) + 1,
                "title": entry.get("title", "N/A"),
                "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                "channel": entry.get("channel") or entry.get("uploader", "N/A"),
                "views": views_str,
                "duration": duration_str,
                "video_id": entry.get("id", ""),
            }
        )

    return results


def format_table(results: list[dict]) -> str:
    lines = [
        f"{'#':<4} {'Title':<60} {'Channel':<30} {'Views':<12} {'Duration':<10} URL",
        "-" * 140,
    ]
    for r in results:
        title = r["title"][:57] + "..." if len(r["title"]) > 60 else r["title"]
        channel = r["channel"][:27] + "..." if len(r["channel"]) > 30 else r["channel"]
        lines.append(
            f"{r['rank']:<4} {title:<60} {channel:<30} {r['views']:<12} {r['duration']:<10} {r['url']}"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search YouTube and return video metadata")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--count", type=int, default=25, help="Number of results (default: 25)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = search_youtube(args.query, args.count)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nYouTube search results for: \"{args.query}\" ({len(results)} videos)\n")
        print(format_table(results))
        print(f"\nURLs only:")
        for r in results:
            print(f"  {r['rank']}. {r['url']}")


if __name__ == "__main__":
    main()
