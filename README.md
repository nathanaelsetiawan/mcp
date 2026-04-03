## mcp-linkedin

This project exposes an MCP tool that searches for LinkedIn candidate profiles using Exa.ai.

### Run

Program:
uv run main.py

MCP Inspector:
uv run mcp dev main.py


Server:
- `http://127.0.0.1:8000`
- MCP endpoint: `http://127.0.0.1:8000/mcp`

### MCP Tool

Tool name (from `operation_id`):
- `search_linkedin_candidates`

Inputs:
- `query` (string): natural-language candidate requirements (role + location + skills, etc.)
- `num_results` (int, 1-10)

Output (JSON):
- `query`
- `total_found`
- `candidates[]` with:
  - `title`
  - `profile_url`
  - `score` (optional)
  - `published_date` (optional)

### Environment

Required:
- `EXA_API_KEY`

