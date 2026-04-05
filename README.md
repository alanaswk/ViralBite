# ViralBite

ViralBite is a multi-agent creator intelligence app for food YouTube topics.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set environment variables:

- `YOUTUBE_API_KEY`
- `OPENAI_API_KEY` (for creator brief + chat)

## Product flow

1. **Collect**: pull topic-matched YouTube videos and comments from the API.
2. **EDA**: compute structured trend metrics for creator decision making.
3. **Hypothesize**: generate a creator brief with concrete recommendations.

## Architecture (LangGraph)

State machine in `app/graph.py` with three nodes:

- `collector_node` (`app/agents.py`): fetches topic data.
- `analyst_node` (`app/agents.py`): computes analysis features.
- `insight_node` (`app/agents.py`): calls LLM for creator brief.

State schema: `app/graph_state.py`.

## File map by rubric step

- **Graph wiring**: `app/utils.py` invokes `build_graph().invoke(...)`
- **Upload frequency**: `analyze_upload_frequency()` in `app/analysis_tools.py`
- **Comment sentiment (VADER)**: `analyze_comment_sentiment()` in `app/analysis_tools.py`
- **Sponsored vs organic**: `analyze_sponsorship()` in `app/analysis_tools.py`
- **LLM creator brief**: `generate_creator_brief()` in `app/llm_client.py`
- **Chat backend**: `POST /chat` in `app/main.py` using `chat_with_analysis_context()`
- **Dashboard UI + chat UI**: `app/templates/index.html`, `app/static/app.js`, `app/static/styles.css`

## Two grab-bags used

- **Structured output with Pydantic schemas**:
  - `CreatorBrief` schema in `app/llm_client.py`
  - request schemas for chat in `app/main.py`
- **Data visualization**:
  - Chart.js frontend charts (duration, upload frequency, sponsorship donut)
  - metric cards/table/keyword and sentiment visual blocks

## Deploy

Deploy as a single FastAPI service on Railway or Render.

- Configure `YOUTUBE_API_KEY` and `OPENAI_API_KEY` in the hosting dashboard.
- Static frontend is already served by FastAPI via `StaticFiles`.
