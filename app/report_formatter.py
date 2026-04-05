def format_report(query: str, analysis: dict, final_response: dict | None = None) -> str:
    summary = analysis.get("summary", {})
    duration_patterns = analysis.get("duration_patterns", [])
    keyword_patterns = analysis.get("keyword_patterns", [])
    creator_brief = (final_response or {}).get("creator_brief", {})
    brief_summary = creator_brief.get("summary", "No creator brief generated.")
    recommendations = creator_brief.get("recommendations", [])

    top_duration = None
    if duration_patterns:
        valid_rows = [row for row in duration_patterns if row.get("video_count", 0) > 0]
        if valid_rows:
            top_duration = max(valid_rows, key=lambda x: x.get("avg_engagement_rate", 0))

    top_keyword = None
    if keyword_patterns:
        top_keyword = max(keyword_patterns, key=lambda x: x.get("avg_engagement_rate", 0))

    lines = []
    lines.append(f"VIRALBITE REPORT: {query.upper()}")
    lines.append("=" * 50)

    lines.append("\nOVERVIEW")
    lines.append(f"- Videos analyzed: {summary.get('num_videos', 'N/A')}")
    lines.append(f"- Average views: {round(summary.get('avg_views', 0), 1)}")
    lines.append(f"- Median views: {round(summary.get('median_views', 0), 1)}")
    lines.append(f"- Average engagement rate: {round(summary.get('avg_engagement_rate', 0), 4)}")

    if top_duration:
        lines.append("\nTOP FORMAT SIGNAL")
        lines.append(f"- Best duration bucket: {top_duration.get('duration_bucket')}")
        lines.append(f"- Avg engagement rate in that bucket: {round(top_duration.get('avg_engagement_rate', 0), 4)}")

    if top_keyword:
        lines.append("\nTOP KEYWORD SIGNAL")
        lines.append(f"- Strongest keyword: {top_keyword.get('keyword')}")
        lines.append(f"- Avg engagement rate: {round(top_keyword.get('avg_engagement_rate', 0), 4)}")
        lines.append(f"- Matching videos: {top_keyword.get('video_count', 0)}")

    lines.append("\nCREATOR BRIEF")
    lines.append(f"- {brief_summary}")

    if recommendations:
        lines.append("\nACTION RECOMMENDATIONS")
        for item in recommendations:
            lines.append(f"- {item}")

    if top_duration or top_keyword:
        lines.append("\nCREATOR TAKEAWAY")
        takeaway = "For this topic, creators should lean into"
        pieces = []

        if top_duration:
            pieces.append(f"{top_duration.get('duration_bucket')} videos")
        if top_keyword:
            pieces.append(f"keyword framing around '{top_keyword.get('keyword')}'")

        lines.append(f"- {takeaway} " + " and ".join(pieces) + ".")

    return "\n".join(lines)