from dotenv import load_dotenv
from api.configs import PostAPIConfigs, SchemaConfigs
from dataloader.load_data import DataLoader
import os
from etl.extract_posts_comments import CommentExtractor

load_dotenv()


def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is not set or empty.")
    return value


def etl_comments():
    # DB CONFIGS
    USER = get_env_variable("user")
    PASSWORD = get_env_variable("password")
    HOST = get_env_variable("host")
    PORT = get_env_variable("port")
    DBNAME = get_env_variable("dbname")

    loader = DataLoader(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )

    # Reddit configs
    reddit_username = get_env_variable("reddit_username")
    SUBREDDIT_NAME = PostAPIConfigs.subreddit_name
    CLIENT_ID = get_env_variable("client_id")
    SECRET = get_env_variable("secret")
    TIMEOUT = PostAPIConfigs.timeout
    USER_AGENT = f"script:{SUBREDDIT_NAME}:1.0 (by u/{reddit_username})"
    POST_LIMIT = PostAPIConfigs.post_limit

    try:
        CE = CommentExtractor(
            subreddit_name=SUBREDDIT_NAME,
            client_id=CLIENT_ID,
            secret=SECRET,
            timeout=TIMEOUT,
            user_agent=USER_AGENT,
            post_limit=POST_LIMIT,
        )

        print("Fetching comment data from posts...")
        comment_data = CE.fetch_comment_data(loader=loader)

        loader = DataLoader(
            user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
        )

        print("Writing comments to remote database...")

        loader.write_data(
            table_name="comments",
            data_rows=comment_data,
            column_names=SchemaConfigs.table_mapping["comments"],
            write_method="upsert",
            upsert_on=["id"],
        )

    except Exception as e:
        print(f"An error occurred {e}")


if __name__ == "__main__":
    etl_comments()
