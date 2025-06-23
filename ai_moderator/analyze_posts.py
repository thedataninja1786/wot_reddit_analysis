from dataloader.load_data import DataLoader
from typing import List, Dict, Any, Tuple, Optional
from ai_moderator.chatbot import AIModerator


class PostAnalyzer:
    def find_new_posts(
        self, loader: DataLoader, post_limit: int
    ) -> List[Dict[str, Any]]:
        """Retrieves the most recent posts that have not yet been analyzed."""

        try:
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
                WHERE category IS NOT NULL
                ORDER BY created_utc DESC
                LIMIT {post_limit}
            );
            """
            posts_df = loader.query_table(q)
            return posts_df.to_dict("records")
        except Exception as e:
            print(f"{self.__class__.__name__} - {self.find_new_posts.__name__}")
            print(f"[ERROR] occurred {e}")
            return []

    def process_posts(
        self, moderator: AIModerator, posts: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, str, str, str, Optional[str], Optional[str], Any]]:
        """
        Performs ai analysis and creates embeddings for a new post and return a row-tuple for upsert.
        """
        res = []

        for post in posts:
            try:
                analysis = moderator.generate_sentiment(
                    flair=post["flair"],
                    title=post["title"],
                    selftext=post["selftext"],
                )
                text = post["selftext"] if post["selftext"] else post["flair"] + post["title"]
                embeddings = moderator.generate_embeddings(text=text)
                res.append(
                    (
                        post["id"],
                        post["title"],
                        post["author"],
                        post["flair"],
                        post["selftext"],
                        analysis.get("category"),
                        analysis.get("reasoning"),
                        post["created_utc"],
                        embeddings,
                    )
                )
            except Exception as e:
                # TODO log properly in side-outputs
                print(f"{self.__class__.__name__} - {self.process_posts.__name__}")
                print(f"[ERROR] occurred when processing post {post['id']}: {e}")

        return res
