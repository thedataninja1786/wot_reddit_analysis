from dataloader.load_data import DataLoader
from datetime import datetime
from praw.models.reddit.submission import Submission
from praw.models.reddit.comment import Comment
from praw import Reddit
from typing import Tuple, List, Any


class CommentExtractor:
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

    def _create_reddit(self) -> Reddit:
        """Creates and returns a PRAW reddit instance for the specified subreddit."""

        return Reddit(
            client_id=self.client_id,
            client_secret=self.secret,
            user_agent=self.user_agent,
            timeout=self.timeout,
        )

    def _process_comments(
        self, post_id: str, submission: Submission
    ) -> List[Tuple[Any]]:
        """
        Processes all comments in a Reddit submission, traversing the comment tree recursively.
        Args:
            post_id (str): The ID of the Reddit post (submission) to which the comments belong.
            submission (Submission): The PRAW Submission object representing the Reddit post.
        Returns:
            List[Tuple[Any]]: A list of tuples, each containing information about a comment:
                (
                    comment.id (str),
                    post_id (str),
                    parent_id (str),
                    comment.body (str),
                    comment.author (str),
                    comment.score (int),
                    comment.created_utc (str, formatted as "%Y-%m-%d_%H:%M:%S")
                )
        """
        submission.comments.replace_more(limit=None)
        all_comments = []
        failed_comments = []

        def walk_comments(comment: Comment, parent_id=None):
            try:
                all_comments.append(
                    (
                        comment.id,
                        post_id,
                        parent_id or submission.id,
                        comment.body,
                        str(comment.author) if comment.author else "deleted",
                        comment.score,
                        datetime.utcfromtimestamp(comment.created_utc).strftime(
                            "%Y-%m-%d_%H:%M:%S"
                        ),
                    )
                )
            except Exception as e:
                print(f"[ERROR] processing comment {comment.id}: {e}")
                failed_comments.append(comment.id)

            for reply in comment.replies:
                walk_comments(reply, parent_id=comment.id)

        for top_level_comment in submission.comments:
            walk_comments(top_level_comment)

        if failed_comments:
            print(
                f"[WARNING] Skipped {len(failed_comments)} comments under post {post_id}: {failed_comments}"
            )

        return all_comments

    def _create_submissions(self, loader: DataLoader) -> List[Tuple[str, Submission]]:
        """
        Fetches the most recent `n` Reddit submissions from the database and returns them as a list of tuples.
        """
        submissions = []

        # get the most recent n posts
        reddit = self._create_reddit()
        q = f"""select id from posts order by created_utc asc limit {self.post_limit}"""
        df = loader.query_table(q)
        post_ids = df["id"].to_list()
        for post_id in post_ids:
            try:
                submission = reddit.submission(id=post_id)
                submissions.append((post_id, submission))
            except Exception as e:
                print(f"Failed to fetch submission with id {post_id}: {e}")

        return submissions

    def fetch_comment_data(self, loader: DataLoader) -> List[Tuple[Any]]:
        """Fetches and processes comment data for a set of Reddit submissions."""

        comment_data_tuples = []
        submissions = self._create_submissions(loader=loader)
        for post_id, submission in submissions:
            comment_data_tuples.extend(self._process_comments(post_id, submission))

        return comment_data_tuples
