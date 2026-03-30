from youtube_collector import collect_youtube_data

import json

def main():
    query = input("Enter a topic (e.g., 'nyc bagel'): ")
    videos = collect_youtube_data(
        query=query,
        max_results=5,
        max_comments_per_video=5,
        fetch_comments=True
    )

    print(f"\nFound {len(videos)} videos:\n")

    for v in videos:
        print(json.dumps(v, indent=2))
        print("-" * 60)

if __name__ == "__main__":
    main()

# def main():
#     query = input("Enter a topic (e.g., 'nyc bagel'): ")

#     videos = collect_youtube_data(query, max_results=5)

#     print(f"\nFound {len(videos)} videos:\n")

#     for v in videos:
#         print("----------")
#         print(f"Video ID: {v['video_id']}")
#         print(f"Title: {v['title']}")
#         print(f"Channel: {v['channel']}")
#         print(f"Published: {v['published_at']}")
#         print(f"Views: {v['views']}")
#         print(f"Likes: {v['likes']}")
#         print(f"Comment Count: {v['comment_count']}")
    
#         print("Top Comments:")
#         for c in v["comments_text"]:
#             print(f"  - {c}")
        
#         print()

# if __name__ == "__main__":
#     main()