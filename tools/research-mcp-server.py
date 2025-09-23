import json
import os
from typing import List

import arxiv
from mcp.server import FastMCP
from dataclasses import asdict, dataclass
from typing import Optional

PAPER_DIR = "papers"
mcp = FastMCP("research")

@dataclass
class SearchResult:
    paper_id: str
    title: str
    published: str

@dataclass
class SearchResults:
    results: List[SearchResult]
    total: int

@dataclass
class Article:
    title: str
    authors: List[str]
    summary: str
    published: str
    pdf_url: str

def _load_papers_info(file_path: str) -> dict:
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_papers_info(file_path: str, data: dict) -> None:
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)

@mcp.tool(name="search_papers", description="Search for papers related to a topic")
def search_papers(topic: str, max_results: int = 5) -> SearchResults:
    client = arxiv.Client()

    search = arxiv.Search(query=topic, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    papers = client.results(search)
    # Create a directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    papers_info=_load_papers_info(file_path)

    # Process each paper and add to papers_info
    results: List[SearchResult]=[]
    for paper in papers:
        paper_id=paper.get_short_id()
        results.append(
            SearchResult(
                paper_id=paper_id,
                title=paper.title,
                published=str(paper.published.date()),
            )
        ) # Build the full "article" to persist
        article = Article(
            title=paper.title,
            authors=[author.name for author in paper.authors],
            summary=paper.summary,
            pdf_url=paper.pdf_url,
            published=str(paper.published.date()),
        )
        papers_info[paper_id] = asdict(article)

    # Save updated papers_info to JSON file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)

    print(f"Results are saved in: {file_path}")

    return SearchResults(results=results, total=len(results))



@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
        Search for information about a specific paper across all topic directories.

        Args:
            paper_id: The ID of the paper to look for

        Returns:
            JSON string with paper information if found, error message if not found
        """

    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

    return f"There's no saved information related to paper {paper_id}."


if __name__ == "__main__":
    mcp.run(transport='stdio')
