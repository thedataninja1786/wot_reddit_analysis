import json
from openai import OpenAI
from typing import Optional, Dict

class AIModerator:
    def __init__(self, client: OpenAI):
        self.client = client

    def _generate_prompt(self, flair: str, title: str, selftext: str) -> str:
        """Generates a prompt for categorizing a Reddit post into predefined categories
        with justification, formatted for an AI moderator assistant."""

        prompt = (
            "You are an AI moderator assistant for the subreddit r/WorldofTanks.\n"
            "Use all of your knowledge about the game and its fanbase, and given "
            "a Reddit post, categorize it into one of the following classes:\n\n"
            "1. Positive Experience\n"
            "2. Negative Experience\n"
            "3. Constructive Feedback\n"
            "4. Bug/Issue Report\n"
            "5. Community/Discussion\n"
            "6. Sarcasm/Humor\n"
            "7. News/Update Sharing\n"
            "8. Question/Help Request\n"
            "9. Off-topic/Other\n\n"
            f"Here is the post:\n"
            f"Flair: {flair}\n"
            f"Title: {title}\n"
            f"Body: {selftext}\n\n"
            "Respond with the best matching category and a short one-sentence justification. "
            "Respond in a JSON (OMIT MARKDOWN) in dictionary format with keys 'category' and 'reasoning'."
        )
        return prompt

    def generate_sentiment(
        self, flair: Optional[str], title: str, selftext: Optional[str]
    ) -> Dict[str, str]:
        """
        Generates sentiment analysis results for a given Reddit post's flair, title, and body using an AI model.
        """

        if not selftext and not flair:
            return {}

        prompt = self._generate_prompt(flair=flair, title=title, selftext=selftext)

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",
            )

            response = response.choices[0].message.content
            return dict(json.loads(response))

        except Exception as e:
            print(
                f"{self.generate_sentiment.__name__} [ERROR] - generate sentiment failed: {e}"
            )
            return {}
