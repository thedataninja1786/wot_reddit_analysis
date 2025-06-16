import praw
from typing import List, Dict, Tuple, Any
from datetime import datetime
from praw.models import Subreddit


class PostExtractor:
    def __init__(
        self,
        subreddit_name: str,
        client_id: str,
        secret: str,
        timeout: int,
        user_agent: str,
        post_limit: int,
    ) -> None:
        self.subreddit_name = subreddit_name
        self.client_id = client_id
        self.secret = secret
        self.timeout = timeout
        self.user_agent = user_agent
        self.post_limit = post_limit

    def _create_subreddit(self) -> Subreddit:
        """Creates and returns a PRAW Subreddit instance for the specified subreddit."""

        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.secret,
            user_agent=self.user_agent,
            timeout=self.timeout,
        ).subreddit(self.subreddit_name)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"subreddit='{self.subreddit_name}', "
            f"client_id='***', "
            f"secret='***', "
            f"timeout={self.timeout}, "
            f"user_agent='{self.user_agent}', "
            f"post_limit={self.post_limit})"
        )

    def fetch_post_data(self) -> List[Tuple[Any]]:
        """
        Fetches post data from the specified subreddit.
        Iterates through the newest posts up to the given limit,
        extracting relevant information from each submission and returning it as a list of dictionaries.
        If an exception occurs while processing a submission, logs the error details.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing data for a single post:
                - id (str): The unique identifier of the post.
                - title (str): The title of the post.
                - author (Optional[str]): The username of the post's author, or None if deleted.
                - selftext (str): The body text of the post.
                - subreddit (str): The name of the subreddit.
                - score (int): The score (upvotes - downvotes) of the post.
                - num_comments (int): The number of comments on the post.
                - created_utc (str): The UTC creation time of the post in "%Y-%m-%d_%H:%M:%S" format.
        """

        post_data = []
        try:
            subreddit = self._create_subreddit()
        except Exception as e:
            print(f" [ERROR] Failed to create subreddit instance: {e}")
            raise

        for submission in subreddit.new(limit=self.post_limit):
            try:
                post_data.append(
                    (
                        submission.id,
                        submission.title,
                        str(submission.author) if submission.author else "unknown",
                        submission.link_flair_text or "",
                        submission.selftext or "",
                        str(submission.subreddit),
                        submission.score or 0,
                        submission.num_comments or 0,
                        datetime.utcfromtimestamp(submission.created_utc).strftime(
                            "%Y-%m-%d_%H:%M:%S"
                        )
                        if submission.created_utc
                        else None,
                    )
                )
            except Exception as e:
                print(
                    f" [ERROR] processing post {getattr(submission, 'id', 'unknown')}: {e}"
                )

        return post_data
