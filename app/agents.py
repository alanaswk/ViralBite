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
    max_results = int(state.get("max_results", 25))
    max_comments_per_video = int(state.get("max_comments_per_video", 10))
    order = state.get("order", "relevance")
    window_days = state.get("window_days", 30)
    max_pages = int(state.get("max_pages", 1))

    videos = collect_youtube_data(
        query=query,
        max_results=max_results,
        max_comments_per_video=max_comments_per_video,
        fetch_comments=True,
        order=order,
        window_days=window_days,
        max_pages=max_pages,
    )

    videos_with_comments = sum(1 for video in videos if video.get("top_comments"))
    collection_meta = {
        "max_results": max_results,
        "max_comments_per_video": max_comments_per_video,
        "order": order,
        "window_days": int(window_days) if window_days is not None else None,
        "max_pages": max_pages,
        "fetched_videos": len(videos),
        "videos_with_comments": videos_with_comments,
    }

    return {"videos": videos, "collection_meta": collection_meta}


def analyst_node(state):
    videos = state["videos"]
    collection_meta = state.get("collection_meta", {})
    df = videos_to_dataframe(videos)

    analysis = {
        "summary": summarize_dataset(df),
        "duration_patterns": analyze_duration_patterns(df),
        "upload_frequency": analyze_upload_frequency(df),
        "keyword_patterns": analyze_keyword_patterns(
            df,
            [
                "cheap", "best", "authentic", "hidden", "local",
                "ranking", "review", "vs", "worth it", "street food",
                "food tour", "honest",
            ],
            top_n=8,
        ),
        "comment_sentiment": analyze_comment_sentiment(df),
        "sponsorship": analyze_sponsorship(df),
        "top_videos": analyze_top_videos(df, top_n=5),
        "sample_definition": {
            "window_days": collection_meta.get("window_days"),
            "order": collection_meta.get("order", "relevance"),
            "fetched_videos": collection_meta.get("fetched_videos", len(videos)),
            "videos_with_comments": collection_meta.get("videos_with_comments", 0),
            "comment_policy": (
                f"Up to {collection_meta.get('max_comments_per_video', 0)} top comments "
                f"per video on {collection_meta.get('videos_with_comments', 0)} videos."
            ),
        },
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