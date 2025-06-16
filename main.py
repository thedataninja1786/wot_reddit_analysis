from etl.ai_analysis import analyze_posts
from etl.extract_load_posts import etl_posts
from etl.extract_load_comments import etl_comments

def main():
    etl_posts()
    analyze_posts()
    etl_comments()

if __name__ == "__main__":
    main()
