#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context  # 可選：回報進度/記錄
from .scraper import ConstituteScraper

mcp = FastMCP("constitute-mcp")
scraper = ConstituteScraper(delay=1)

@mcp.tool()
def get_constitutions_list(show_details: bool = False, region_filter: Optional[str] = None) -> dict:
    """Get a list of available constitutions. Optionally filter by region."""
    constitutions = scraper.get_constitutions_list()
    if region_filter:
        constitutions = [c for c in constitutions if c.get("region", "").lower() == (region_filter or "").lower()]
    if show_details:
        return {"total_count": len(constitutions), "constitutions": constitutions}
    return {"total_count": len(constitutions), "countries": [c.get("country", "Unknown") for c in constitutions]}

@mcp.tool()
def find_constitution_by_country(country_name: str, exact_match: bool = False) -> dict:
    """Find constitutions by country name."""
    matches = scraper.find_constitution_by_country(country_name, exact_match)
    return {"query": country_name, "exact_match": exact_match, "found_count": len(matches), "matches": matches}

@mcp.tool()
def scrape_constitution(constitution_id: str) -> dict:
    """Scrape and cache a constitution. Returns a summary."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to scrape constitution: {constitution_id}")
    return {
        "message": f"Successfully scraped constitution: {constitution_id}",
        "summary": {
            "id": content.get("id"),
            "title": content.get("title"),
            "preamble_length": len(content.get("preamble", "")),
            "chapters_count": len(content.get("chapters", [])),
            "articles_count": len(content.get("articles", [])),
            "full_text_length": len(content.get("full_text", "")),
        },
        "note": "Full content cached on server; call other tools to fetch sections/articles."
    }

@mcp.tool()
def get_article_by_number(constitution_id: str, article_number: str) -> dict:
    """Get a specific article by number."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to get constitution content: {constitution_id}")
    article = scraper.get_article_by_number(content, article_number)
    if article is None:
        return {"message": f"Article {article_number} not found", "constitution_id": constitution_id}
    return article

@mcp.tool()
def get_articles_range(constitution_id: str, start_article: str, end_article: str) -> dict:
    """Get a range of articles."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to get constitution content: {constitution_id}")
    articles = scraper.get_articles_range(content, start_article, end_article)
    return {"constitution_id": constitution_id, "range": f"{start_article}-{end_article}", "found_count": len(articles), "articles": articles}

@mcp.tool()
def search_articles_by_keyword(constitution_id: str, keyword: str) -> dict:
    """Search articles by keyword."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to get constitution content: {constitution_id}")
    articles = scraper.search_articles_by_keyword(content, keyword)
    return {"constitution_id": constitution_id, "keyword": keyword, "found_count": len(articles), "articles": articles}

@mcp.tool()
def topic_constitutions(topic_key: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all") -> dict:
    """Find constitutions by topic key (e.g. 'econplan','env','leg')."""
    constitutions = scraper.topic_constitutions(topic_key, in_force=in_force, is_draft=is_draft, ownership=ownership)
    return {"topic_key": topic_key, "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership}, "found_count": len(constitutions), "constitutions": constitutions}

@mcp.tool()
def topic_sections(topic_key: str, constitution_id: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all") -> dict:
    """Get topic-related sections from a constitution."""
    sections = scraper.topic_sections(topic_key, constitution_id, in_force=in_force, is_draft=is_draft, ownership=ownership)
    return {"topic_key": topic_key, "constitution_id": constitution_id, "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership}, "found_count": len(sections), "sections": sections}

@mcp.tool()
def export_constitution_json(constitution_id: str, filename: Optional[str] = None) -> str:
    """Export constitution as JSON file on the server filesystem."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to get constitution content: {constitution_id}")
    filename = scraper.sanitize_filename(filename or f"{constitution_id}.json")
    scraper.save_to_json(content, filename)
    return f"Constitution {constitution_id} exported to {filename}"

@mcp.tool()
def export_constitution_text(constitution_id: str, filename: Optional[str] = None) -> str:
    """Export constitution as plain text on the server filesystem."""
    content = scraper.scrape_constitution_content(constitution_id)
    if content is None:
        raise RuntimeError(f"Failed to get constitution content: {constitution_id}")
    filename = scraper.sanitize_filename(filename or f"{constitution_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content.get("full_text", ""))
    return f"Constitution {constitution_id} exported as text to {filename}"

if __name__ == "__main__":
    # 使用 stdio 傳輸供本機 host（例如 Claude 桌面版）連線
    mcp.run(transport="stdio")
