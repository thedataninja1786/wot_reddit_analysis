from dotenv import load_dotenv
from api.configs import PostAPIConfigs, SchemaConfigs
from dataloader.load_data import DataLoader
from utils.utilities import get_env_variable
from extractors.extract_posts_comments import CommentExtractor

load_dotenv()

# DB CONFIGS
USER = get_env_variable("DB_USER")
PASSWORD = get_env_variable("DB_PASSWORD")
HOST = get_env_variable("DB_HOST")
PORT = get_env_variable("DB_PORT")
DBNAME = get_env_variable("DB_NAME")

loader = DataLoader(
    user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
)

# Reddit configs
REDDIT_USERNAME = get_env_variable("REDDIT_USERNAME")
SUBREDDIT_NAME = PostAPIConfigs.subreddit_name
CLIENT_ID = get_env_variable("CLIENT_ID")
SECRET = get_env_variable("CLIENT_SECRET")
TIMEOUT = PostAPIConfigs.timeout
USER_AGENT = f"script:{SUBREDDIT_NAME}:1.0 (by u/{REDDIT_USERNAME})"
POST_LIMIT = PostAPIConfigs.post_limit

def etl_comments():    
    print("Running comments etl...")
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

        print("Writing comments to remote database...")

        loader.write_data(
            table_name="comments",
            data_rows=comment_data,
            column_names=SchemaConfigs.table_mapping["comments"],
            write_method="upsert",
            upsert_on=["id"],
        )

    except Exception as e:
        print(f"{etl_comments.__name__} - [ERROR] An error occurred {e}")


if __name__ == "__main__":
    etl_comments()
