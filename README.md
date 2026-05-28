## mcp-linkedin

This project exposes an MCP tool that searches for LinkedIn candidate profiles using Exa.ai.

### Run

Program:
uv run python main.py

MCP Inspector:
npx @modelcontextprotocol/inspector python main.py


Server:
- `http://0.0.0.0:5001`
- MCP endpoint: `http://0.0.0.0:5001/sse`

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

