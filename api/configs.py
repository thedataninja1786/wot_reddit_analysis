class PostAPIConfigs:
    subreddit_name = "WorldofTanks"
    timeout = 10
    ratelimit_seconds = 60
    post_limit = 150

class SchemaConfigs:
    table_mapping = {
        "posts":[
            "id",
            "title",
            "author",
            "flair",
            "selftext",
            "subreddit",
            "score",
            "num_comments",
            "created_utc"
        ],
        "comments":[
            "id",
            "post_id",
            "parent_id",
            "body",
            "author",
            "score",
            "created_utc"
        ],
        "posts_ai_analysis":[
            "id",
            "title",
            "author",
            "flair",
            "selftext",
            "category",
            "reasoning",
            "created_utc"
        ]
    }   