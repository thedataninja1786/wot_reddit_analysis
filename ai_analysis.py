from ai_moderator.chatbot import AIModerator
from dotenv import load_dotenv
from typing import Tuple, Optional
from openai import OpenAI
from dataloader.load_data import DataLoader
from typing import List, Dict, Any
import asyncio
from api.configs import SchemaConfigs, PostAPIConfigs
from utils.utilities import get_env_variable

load_dotenv()

def find_new_posts(loader: DataLoader,post_limit:int) -> List[Dict[str, Any]]:
    
    q = f"""
    WITH recent_posts AS (
        SELECT
            id,
            title,
            author,
            flair,
            selftext,
            created_utc
        FROM posts
        ORDER BY created_utc DESC
        LIMIT {post_limit}
    )
    SELECT *
    FROM recent_posts
    WHERE id NOT IN (
        SELECT id
        FROM posts_ai_analysis
        where category is NOT NULL
        ORDER BY created_utc DESC
        limit {post_limit}
    );
    """
    posts_df = loader.query_table(q)
    return posts_df.to_dict("records")


def process_post(moderator: AIModerator, post: Dict[str, Any]) -> Tuple[str, str, str, str, str, Optional[str], Optional[str], Any]:
    """
    Fetch ai analysis for new post and return a row-tuple for upsert.
    """
    analysis = moderator.generate_sentiment(
        flair=post["flair"],
        title=post["title"],
        selftext=post["selftext"],
    )
    return (
        post["id"],
        post["title"],
        post["author"],
        post["flair"],
        post["selftext"],
        analysis.get("category"),
        analysis.get("reasoning"),
        post["created_utc"]
    )

def main():

    OPENAI_KEY = get_env_variable("API_KEY")

    CLIENT = OpenAI(api_key=OPENAI_KEY)

    USER = get_env_variable("user")
    PASSWORD = get_env_variable("password")
    HOST = get_env_variable("host")
    PORT = get_env_variable("port")
    DBNAME = get_env_variable("dbname")

    POST_LIMIT = PostAPIConfigs.post_limit

    loader = DataLoader(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )

    ai_mod = AIModerator(client = CLIENT)

    new_posts = find_new_posts(loader = loader, post_limit = POST_LIMIT)
    print(f"Found {len(new_posts)} posts to analyze.")
    
    results = []
    for post in new_posts:
        results.append(process_post(moderator = ai_mod, post = post))

    print(f"{len(results)} have been processed.")

    print("Writing data to remote database...")

    loader.write_data(
    table_name="posts_ai_analysis",
    data_rows=results,
    column_names=SchemaConfigs.table_mapping["posts_ai_analysis"],
    write_method="upsert",
    upsert_on=["id"],
    )


if __name__ == "__main__":
    main()