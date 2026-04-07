import os
from functools import lru_cache
from typing import List, Optional
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from exa_py import Exa
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel

load_dotenv()

# 1. FIX: Initialize with a string name, not the 'app' object
mcp = FastMCP("linkedin-mcp-server")

app = FastAPI()

# 2. FIX: Mount to a specific path to avoid root conflicts
app.mount("/", mcp.streamable_http_app())

@lru_cache(maxsize=1)
def get_exa():
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not found in environment")
    return Exa(api_key)

class Candidate(BaseModel):
    title: str
    profile_url: str
    score: Optional[float] = None

class LinkedInSearchResponse(BaseModel):
    query: str
    total_found: int
    candidates: List[Candidate]

@mcp.tool()
def search_linkedin_candidates(query: str, num_results: int = 5) -> LinkedInSearchResponse:
    """Mencari profil kandidat di LinkedIn."""
    if not query.strip():
        raise ValueError("`query` must not be empty.")
    
    num_results = max(1, min(num_results, 10))
    include_domains = ["linkedin.com/in/"]
    
    try:
        exa = get_exa()
        response = exa.search(
            query,
            num_results=num_results,
            include_domains=include_domains,
            type="neural",
            # use_autoprompt=True
        )
        
        candidates = [
            Candidate(
                title=getattr(r, "title", "No Title"),
                profile_url=getattr(r, "url", ""),
                score=getattr(r, "score", 0.0)
            ) for r in response.results
        ]
        
        return LinkedInSearchResponse(
            query=query,
            total_found=len(candidates),
            candidates=candidates
        )
    except Exception as e:
        raise RuntimeError(f"Exa search failed: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

# 3. FIX: Only use uvicorn.run(). DO NOT use mcp.run() here.
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting MCP Server on http://{host}:{port}/mcp")
    mcp.run("streamable-http")
    # uvicorn.run(app, host=host, port=port)