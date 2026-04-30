from pydantic import BaseModel
from typing import Optional, List

class Candidate(BaseModel):
    title: str
    profile_url: str
    score: Optional[float] = None
    published_date: Optional[str] = None

class LinkedInSearchResponse(BaseModel):
    query: str
    total_found: int
    candidates: List[Candidate]