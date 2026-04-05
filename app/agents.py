from app.youtube_collector import collect_youtube_data
from app.analysis_tools import (
    videos_to_dataframe,
    summarize_dataset,
    analyze_duration_patterns,
    analyze_upload_frequency,
    analyze_keyword_patterns,
    analyze_comment_sentiment,
    analyze_sponsorship,
    analyze_top_videos,
)
from app.llm_client import generate_creator_brief


def collector_node(state):
    query = state["query"]

    videos = collect_youtube_data(
        query=query,
        max_results=20,
        max_comments_per_video=10,
        fetch_comments=True
    )

    return {"videos": videos}


def analyst_node(state):
    videos = state["videos"]
    df = videos_to_dataframe(videos)

    analysis = {
        "summary": summarize_dataset(df),
        "duration_patterns": analyze_duration_patterns(df),
        "upload_frequency": analyze_upload_frequency(df),
        "keyword_patterns": analyze_keyword_patterns(
            df,
            ["cheap", "best", "authentic", "hidden", "local"]
        ),
        "comment_sentiment": analyze_comment_sentiment(df),
        "sponsorship": analyze_sponsorship(df),
        "top_videos": analyze_top_videos(df, top_n=5),
    }

    return {"analysis": analysis}


def insight_node(state):
    analysis = state["analysis"]
    creator_brief = generate_creator_brief(analysis)

    final_response = {
        "summary": analysis["summary"],
        "creator_brief": creator_brief,
    }

    return {"final_response": final_response}