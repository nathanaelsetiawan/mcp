import os
from functools import lru_cache
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http import TransportSecuritySettings
from exa_py import Exa
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

# App and plugin instatiation
app = FastAPI()
mcp = FastMCP(app, "linkedin-mcp-server")

app.mount("/", mcp.streamable_http_app())


@lru_cache(maxsize=1)
def get_exa():
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not found in environment")
    return Exa(api_key)

# Model untuk tiap individu kandidat
class Candidate(BaseModel):
    title: str
    profile_url: str
    score: Optional[float] = None
    published_date: Optional[str] = None

# Model untuk respon keseluruhan
class LinkedInSearchResponse(BaseModel):
    query: str
    total_found: int
    candidates: List[Candidate]

# Endpoint declarations
@mcp.tool()
def search_linkedin_candidates(query: str, num_results: int = 5) -> LinkedInSearchResponse:
    """
    Mencari profil kandidat potensial di LinkedIn menggunakan pencarian neural Exa.ai.
    Tool ini memahami konteks dan makna, bukan sekadar kata kunci.
 
    Args:
        query: Deskripsi kebutuhan kandidat.
        num_results: Jumlah kandidat yang ingin ditampilkan (1-10).
    """
    if not query.strip():
        raise ValueError("`query` must not be empty.")
 
    include_domains = ["linkedin.com/in/"]
 
    try:
        exa = get_exa()
        response = exa.search(
            query,
            num_results=num_results,
            include_domains=include_domains,
            type="neural",   # AI mengambil konteks
            contents=False,  # mengambil url dan judul, bukan data lengkap
        )
 
        results = response.results or []
        candidates: List[Candidate] = []
        for r in results:
            url = getattr(r, "url", None)
            if not url:
                continue
            candidates.append(
                Candidate(
                    title=getattr(r, "title", None) or str(url),
                    profile_url=str(url),
                    score=getattr(r, "score", None),
                )
            )
 
        return LinkedInSearchResponse(
            query=query,
            total_found=len(candidates),
            candidates=candidates,
        )
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exa search failed: {e}")
        # raise ValueError(f"Exa search failed: {e}")

@app.get("/health")
def health():
    return "server bisa dijalankan"

# Entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # mcp.run(transport="streamable-http")