from ai_moderator.chatbot import AIModerator
from ai_moderator.analyze_posts import PostAnalyzer
from dotenv import load_dotenv
from openai import OpenAI
from dataloader.load_data import DataLoader
from api.configs import SchemaConfigs, PostAPIConfigs
from utils.utilities import get_env_variable

load_dotenv()
# Env vars
API_KEY = get_env_variable("API_KEY")
USER    = get_env_variable("DB_USER")
PASSWORD= get_env_variable("DB_PASSWORD")
HOST    = get_env_variable("DB_HOST")
PORT    = get_env_variable("DB_PORT")
DBNAME  = get_env_variable("DB_NAME")
POST_LIMIT = PostAPIConfigs.post_limit

# Clients
client = OpenAI(api_key=API_KEY)
ai_mod = AIModerator(client=client)

# Instances
loader = DataLoader(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    dbname=DBNAME
)
analyzer = PostAnalyzer()

def analyze_posts():
    print("Running analyze posts...")
    try:

        new_posts = analyzer.find_new_posts(loader = loader, post_limit = POST_LIMIT)    

        print(f"Found {len(new_posts)} posts to analyze.")

        results = analyzer.process_posts(moderator = ai_mod,posts = new_posts)   
        if results:

            print(f"{len(results)} have been processed.")
            print("Writing data to remote database...")

            loader.write_data(
            table_name="posts_ai_analysis",
            data_rows=results,
            column_names=SchemaConfigs.table_mapping["posts_ai_analysis"],
            write_method="upsert",
            upsert_on=["id"],
            )
        else:
            print("No results to write; exiting...")
        
    except Exception as e:
        print(f"{analyze_posts.__name__} - [ERROR] An error occurred {e}")


if __name__ == "__main__":
    analyze_posts()