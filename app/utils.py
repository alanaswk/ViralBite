from app.graph import build_graph
from app.report_formatter import format_report


def run_topic_analysis(query: str) -> dict:
    graph = build_graph()
    state = graph.invoke({"query": query})
    analysis = state.get("analysis", {})
    final_response = state.get("final_response", {})
    report = format_report(query, analysis, final_response)

    return {
        "query": query,
        "analysis": analysis,
        "final_response": final_response,
        "report": report,
    }

def build_homepage_cards(topics: list[str]) -> list[dict]:
    return [
        {"topic": topic, "window": "weekly", "source": "hardcoded_demo"}
        for topic in topics
    ]