import os
import re
from typing import Optional
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
    role: str,
    job_description: str,
    must_have: Optional[List[str]] = None,
    nice_to_have: Optional[List[str]] = None,
    region: Optional[str] = None,
    workplace: Optional[str] = None,      # "on-site" | "hybrid" | "remote"
    employment_status: Optional[str] = None, # "full-time" | "contract" | "part-time" | "intern"
    num_results: int = 1
) -> LinkedInSearchResponse:
    """
    Mencari profil kandidat LinkedIn berdasarkan detail lowongan kerja.

    Args:
        role:             Judul posisi, mis. 'Backend Engineer'.
        job_description:  Deskripsi singkat pekerjaan.
        must_have:        Skill wajib dimiliki kandidat.
        nice_to_have:     Skill tambahan yang diinginkan.
        region:           Lokasi kandidat, mis. 'Jakarta', 'Indonesia'.
        workplace:        Tipe lokasi kerja: 'on-site', 'hybrid', atau 'remote'.
        employee_status:  Status karyawan: 'full-time', 'contract', 'part-time', 'intern'.
        disqualifiers:    Kata kunci pendiskualifikasi.
        num_results:      Jumlah kandidat yang diambil (1-10).
    """
    must_have       = must_have or []
    nice_to_have    = nice_to_have or []

    # Build query dari semua field
    parts = [f"{role} professional"]

    if job_description:
        parts.append(job_description.strip())
    if must_have:
        parts.append(f"with expertise in {', '.join(must_have)}")
    if nice_to_have:
        parts.append(f"familiar with {', '.join(nice_to_have)}")
    if region:
        parts.append(f"based in {region}")
    if workplace:
        parts.append(f"{workplace} work")
    if employment_status:
        parts.append(f"{employment_status} position")

    query = " ".join(parts)

    num_results = max(1, min(num_results, 10))

    try:
        exa = get_exa()
    except ValueError as e:
        raise RuntimeError(f"Exa client not configured: {e}") from e

    try:
        response = exa.search_and_contents(
            query,
            num_results=num_results,
            include_domains=["linkedin.com/in/"],
            type="neural",
            text={"max_characters": 400, "include_html_tags": False},
        )
    except Exception as e:
        raise RuntimeError(f"Exa search failed: {e}") from e

    candidates: List[Candidate] = []

    for r in response.results or []:
        if not getattr(r, "url", None):
            continue

        title     = getattr(r, "title", None) or str(r.url)
        snippet   = (getattr(r, "text", None) or "").strip()
        exa_score = getattr(r, "score", None) or 0.0
        blob      = f"{title} {snippet}".lower()

        # Screening
        if any(re.search(r"\b" + re.escape(kw.lower()) + r"\b", blob) for kw in disqualifiers):
            continue

        # Scoring
        if must_have:
            matched     = sum(1 for s in must_have if re.search(r"\b" + re.escape(s.lower()) + r"\b", blob))
            skill_score = matched / len(must_have)
        else:
            skill_score = 1.0

        composite = round(0.6 * skill_score + 0.4 * min(exa_score, 1.0), 4)

        candidates.append(Candidate(
            title=title,
            profile_url=str(r.url),
            score=composite,
        ))

    candidates.sort(key=lambda c: c.score, reverse=True)

    return LinkedInSearchResponse(
        query=query,
        total_found=len(candidates),
        candidates=candidates,
    )

if __name__ == "__main__":
    mcp.run(transport="sse")