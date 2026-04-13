import os
from functools import lru_cache
from typing import List
from dotenv import load_dotenv
from exa_py import Exa
from mcp.server.fastmcp import FastMCP
from models import Candidate, LinkedInSearchResponse

load_dotenv()

mcp = FastMCP("linkedin-mcp-server", host="0.0.0.0")

@lru_cache(maxsize=1)
def get_exa() -> Exa:
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not found in environment variables.")
    return Exa(api_key)


@mcp.tool()
def search_linkedin_candidates(
    query: str,
    num_results: int = 5,
) -> LinkedInSearchResponse:
    """
    Mencari profil kandidat potensial di LinkedIn menggunakan pencarian neural Exa.ai.
    Tool ini memahami konteks dan makna, bukan sekadar kata kunci.

    Args:
        query:       Deskripsi kebutuhan kandidat.
        num_results: Jumlah kandidat yang ingin ditampilkan (1-10).
    """
    if not query.strip():
        raise ValueError("`query` must not be empty.")

    num_results = max(1, min(num_results, 10))

    try:
        exa = get_exa()
    except ValueError as e:
        raise RuntimeError(f"Exa client not configured: {e}") from e

    try:
        response = exa.search(
            query,
            num_results=num_results,
            include_domains=["linkedin.com/in/"],
            type="neural",
            contents=False,
        )
    except Exception as e:
        raise RuntimeError(f"Exa search failed: {e}") from e

    candidates: List[Candidate] = [
        Candidate(
            title=getattr(r, "title", None) or str(r.url),
            profile_url=str(r.url),
            score=getattr(r, "score", None),
        )
        for r in (response.results or [])
        if getattr(r, "url", None)
    ]

    return LinkedInSearchResponse(
        query=query,
        total_found=len(candidates),
        candidates=candidates,
    )

if __name__ == "__main__":
    mcp.run(transport="sse")