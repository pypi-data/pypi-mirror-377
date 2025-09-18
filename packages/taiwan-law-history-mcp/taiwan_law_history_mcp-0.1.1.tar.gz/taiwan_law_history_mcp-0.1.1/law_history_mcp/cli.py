#!/usr/bin/env python3
"""
CLI wrapper for testing the Law History MCP functions
"""

import argparse
import asyncio
import json
import sys

from .server import (
    search_law,
    get_law_history,
    get_law_articles,
    parse_law_text,
    convert_dates,
    normalize_article_number,
)

async def main():
    parser = argparse.ArgumentParser(description="Taiwan Law History CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search law command
    search_parser = subparsers.add_parser("search", help="Search for laws")
    search_parser.add_argument("name", help="Law name to search for")

    # Get history command
    history_parser = subparsers.add_parser("history", help="Get law history")
    history_parser.add_argument("name", help="Exact law name")

    # Get articles command
    articles_parser = subparsers.add_parser("articles", help="Get law articles")
    articles_parser.add_argument("name", help="Exact law name")

    # Parse text command
    parse_parser = subparsers.add_parser("parse", help="Parse law text")
    parse_parser.add_argument("text", help="Text to parse")

    # Convert date command
    date_parser = subparsers.add_parser("date", help="Convert ROC date")
    date_parser.add_argument("date", help="ROC date to convert")

    # Normalize article command
    normalize_parser = subparsers.add_parser("normalize", help="Normalize article number")
    normalize_parser.add_argument("article", help="Article text to normalize")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "search":
            result = await search_law(args.name)
        elif args.command == "history":
            result = await get_law_history(args.name)
        elif args.command == "articles":
            result = await get_law_articles(args.name)
        elif args.command == "parse":
            result = await parse_law_text(args.text)
        elif args.command == "date":
            result = await convert_dates(args.date)
        elif args.command == "normalize":
            result = await normalize_article_number(args.article)
        else:
            print(f"Unknown command: {args.command}")
            return

        # Print the result
        for item in result:
            print(item.text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())