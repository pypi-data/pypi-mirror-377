#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constitute MCP Server - FastMCP Implementation
Constitutional Document Analysis and Scraping Tools

A modern, simplified MCP server using FastMCP framework.
"""

import json
import logging
from typing import Optional, List, Dict, Any

from fastmcp import FastMCP
from .scraper import ConstituteScraper


# Initialize FastMCP server
mcp = FastMCP(
    name="constitute-mcp"
)

# Initialize scraper
scraper = ConstituteScraper(delay=1)
logger = logging.getLogger("constitute_mcp.fastmcp_server")


@mcp.tool()
def get_constitutions_list(
    show_details: bool = False,
    region_filter: Optional[str] = None
) -> str:
    """Get a list of all available constitutions.

    Args:
        show_details: Whether to include detailed information
        region_filter: Filter by region (optional)

    Returns:
        JSON string with constitution list
    """
    try:
        constitutions = scraper.get_constitutions_list()
        if region_filter:
            rf = (region_filter or "").lower()
            constitutions = [c for c in constitutions if c.get("region", "").lower() == rf]

        result: Dict[str, Any] = {"total_count": len(constitutions)}
        if show_details:
            result["constitutions"] = constitutions
        else:
            result["countries"] = [c.get("country", "Unknown") for c in constitutions]

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to get constitutions list: {e}")


@mcp.tool()
def find_constitution_by_country(
    country_name: str,
    exact_match: bool = False
) -> str:
    """Find constitutions by country name.

    Args:
        country_name: Name of the country to search for
        exact_match: Whether to use exact matching

    Returns:
        JSON string with search results
    """
    try:
        matches = scraper.find_constitution_by_country(country_name, exact_match)
        result = {
            "query": country_name,
            "exact_match": exact_match,
            "found_count": len(matches),
            "matches": matches,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to find constitution by country: {e}")


@mcp.tool()
def scrape_constitution(constitution_id: str) -> str:
    """Scrape the full content of a specific constitution.

    Args:
        constitution_id: ID of the constitution to scrape

    Returns:
        JSON string with scraping summary
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to scrape constitution: {constitution_id}")

        summary = {
            "id": content.get("id"),
            "title": content.get("title"),
            "preamble_length": len(content.get("preamble", "")),
            "chapters_count": len(content.get("chapters", [])),
            "articles_count": len(content.get("articles", [])),
            "full_text_length": len(content.get("full_text", "")),
        }
        payload = {
            "message": f"Successfully scraped constitution: {constitution_id}",
            "summary": summary,
            "note": "Full content cached on server. Use specific article/section tools to access content.",
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to scrape constitution: {e}")


@mcp.tool()
def get_article_by_number(constitution_id: str, article_number: str) -> str:
    """Get a specific article from a constitution by its number.

    Args:
        constitution_id: ID of the constitution
        article_number: Article number to retrieve

    Returns:
        JSON string with article content
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

        article = scraper.get_article_by_number(content, article_number)
        if article is None:
            return f"Article {article_number} not found in constitution {constitution_id}"

        return json.dumps(article, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to get article: {e}")


@mcp.tool()
def get_articles_range(
    constitution_id: str,
    start_article: str,
    end_article: str
) -> str:
    """Get a range of articles from a constitution.

    Args:
        constitution_id: ID of the constitution
        start_article: Starting article number
        end_article: Ending article number

    Returns:
        JSON string with articles in range
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

        articles = scraper.get_articles_range(content, start_article, end_article)
        result = {
            "constitution_id": constitution_id,
            "range": f"{start_article}-{end_article}",
            "found_count": len(articles),
            "articles": articles,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to get articles range: {e}")


@mcp.tool()
def search_articles_by_keyword(constitution_id: str, keyword: str) -> str:
    """Search for articles containing specific keywords.

    Args:
        constitution_id: ID of the constitution
        keyword: Keyword to search for

    Returns:
        JSON string with matching articles
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

        articles = scraper.search_articles_by_keyword(content, keyword)
        result = {
            "constitution_id": constitution_id,
            "keyword": keyword,
            "found_count": len(articles),
            "articles": articles,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to search articles: {e}")


@mcp.tool()
def topic_constitutions(
    topic_key: str,
    in_force: bool = True,
    is_draft: bool = False,
    ownership: str = "all"
) -> str:
    """Find constitutions by topic key.

    Args:
        topic_key: Topic key to search for (e.g., 'econplan', 'env', 'leg')
        in_force: Only include constitutions currently in force
        is_draft: Include draft constitutions
        ownership: Ownership filter ('all', 'public', 'mine')

    Returns:
        JSON string with matching constitutions
    """
    try:
        constitutions = scraper.topic_constitutions(
            topic_key, in_force=in_force, is_draft=is_draft, ownership=ownership
        )
        result = {
            "topic_key": topic_key,
            "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
            "found_count": len(constitutions),
            "constitutions": constitutions,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to search constitutions by topic: {e}")


@mcp.tool()
def topic_sections(
    topic_key: str,
    constitution_id: str,
    in_force: bool = True,
    is_draft: bool = False,
    ownership: str = "all"
) -> str:
    """Get specific sections from a constitution related to a topic.

    Args:
        topic_key: Topic key to search for
        constitution_id: ID of the constitution
        in_force: Only include constitutions currently in force
        is_draft: Include draft constitutions
        ownership: Ownership filter ('all', 'public', 'mine')

    Returns:
        JSON string with matching sections
    """
    try:
        sections = scraper.topic_sections(
            topic_key, constitution_id, in_force=in_force, is_draft=is_draft, ownership=ownership
        )
        result = {
            "topic_key": topic_key,
            "constitution_id": constitution_id,
            "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
            "found_count": len(sections),
            "sections": sections,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to get topic sections: {e}")


@mcp.tool()
def export_constitution_json(
    constitution_id: str,
    filename: Optional[str] = None
) -> str:
    """Export constitution data as JSON.

    Args:
        constitution_id: ID of the constitution
        filename: Output filename (optional)

    Returns:
        Success message with filename
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

        if not filename:
            filename = f"{constitution_id}.json"
        filename = scraper.sanitize_filename(filename)
        scraper.save_to_json(content, filename)

        return f"Constitution {constitution_id} exported to {filename}"
    except Exception as e:
        raise RuntimeError(f"Failed to export constitution: {e}")


@mcp.tool()
def export_constitution_text(
    constitution_id: str,
    filename: Optional[str] = None
) -> str:
    """Export constitution as plain text.

    Args:
        constitution_id: ID of the constitution
        filename: Output filename (optional)

    Returns:
        Success message with filename
    """
    try:
        content = scraper.scrape_constitution_content(constitution_id)
        if content is None:
            raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

        if not filename:
            filename = f"{constitution_id}.txt"
        filename = scraper.sanitize_filename(filename)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content.get("full_text", ""))

        return f"Constitution {constitution_id} exported as text to {filename}"
    except Exception as e:
        raise RuntimeError(f"Failed to export constitution as text: {e}")


@mcp.tool()
def scrape_all_constitutions(
    limit: Optional[int] = None,
    save_individual: bool = True
) -> str:
    """Scrape all available constitutions (batch operation).

    Args:
        limit: Limit the number of constitutions
        save_individual: Save individual files

    Returns:
        JSON string with operation summary
    """
    try:
        result = scraper.scrape_all_constitutions(limit=limit, save_individual=save_individual)
        summary = {
            "total_scraped": len(result),
            "limit_applied": limit,
            "individual_files_saved": save_individual,
            "message": f"Successfully scraped {len(result)} constitutions",
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to scrape all constitutions: {e}")


def main():
    """Main entry point for the FastMCP server."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting FastMCP Constitute server...")
    mcp.run()


def cli():
    """CLI entry point configured in pyproject [project.scripts]."""
    main()


if __name__ == "__main__":
    cli()