from api.configs import PostAPIConfigs, SchemaConfigs
from utils.utilities import get_env_variable
from dotenv import load_dotenv
from extractors.extract_posts import PostExtractor
from dataloader.load_data import DataLoader

load_dotenv()

# DB CONFIGS
USER = get_env_variable("user")
PASSWORD = get_env_variable("password")
HOST = get_env_variable("host")
PORT = get_env_variable("port")
DBNAME = get_env_variable("dbname")

# Subreddit Configs
REDDIT_USERNAME = get_env_variable("reddit_username")
SUBREDDIT_NAME = PostAPIConfigs.subreddit_name
CLIENT_ID = get_env_variable("client_id")
SECRET = get_env_variable("secret")
TIMEOUT = PostAPIConfigs.timeout
USER_AGENT = f"script:{SUBREDDIT_NAME}:1.0 (by u/{REDDIT_USERNAME})"
POST_LIMIT = PostAPIConfigs.post_limit

def etl_posts():
    print("Running posts etl...")
    try:
        PE = PostExtractor(
            subreddit_name=SUBREDDIT_NAME,
            client_id=CLIENT_ID,
            secret=SECRET,
            timeout=TIMEOUT,
            user_agent=USER_AGENT,
            post_limit=POST_LIMIT,
        )

        print("Fetching posts...")
        posts_data = PE.fetch_post_data()
        
        loader = DataLoader(
            user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
        )
        print("Writing posts to remote database...")

        loader.write_data(
            table_name="posts",
            data_rows=posts_data,
            column_names=SchemaConfigs.table_mapping["posts"],
            write_method="upsert",
            upsert_on=["id"],
        )
    except Exception as e:
        print(f"{etl_posts.__name__} - [ERROR] An error occurred {e}")

if __name__ == "__main__":
    etl_posts()
