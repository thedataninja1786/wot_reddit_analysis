import json
from openai import OpenAI
from typing import Optional, Dict
import re
import html

class AIModerator:
    def __init__(self, client: OpenAI):
        self.client = client
    
    def clean_comment(self,text: str) -> str:
        if not text:
            return ""
        
        text = text.replace("\n", " ")

        # Unescape HTML entities (e.g. &amp; -> &)
        text = html.unescape(text)

        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # Remove emails (optional, in case you have them)
        text = re.sub(r'\S+@\S+', '', text)

        # Remove HTML tags (in case you have scraped content)
        text = re.sub(r'<.*?>', '', text)

        # Remove emojis and non-ASCII symbols (optional — depends on your needs)
        text = re.sub(r'[^\x00-\x7F]+', '', text)

        # Remove control characters (non-printable ASCII)
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)

        # Normalize multiple spaces and line breaks into single space
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing spaces
        text = text.strip()

        return text

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

    def generate_embeddings(self, text: str):
        """ Creates embeddings for 'selftext' of a post for performing similarity search 
            based on user queries.
        """
        try:
            text = self.clean_comment(text)
            return (
                self.client.embeddings.create(
                    input=[text], model="text-embedding-3-small"
                )
                .data[0]
                .embedding
            )
        except Exception as e:
            print(text)
            print(
                f"{self.generate_embeddings.__name__} [ERROR] - generating embedding failed: {e}"
            )
