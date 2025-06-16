from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from typing import Optional, Dict
import asyncio

load_dotenv()
api_key = os.getenv("API_KEY").strip()

if not api_key:
    raise ValueError("No API key found in environment variables")

client = OpenAI(api_key=api_key)

class AIModerator:
    def __init__(self,client:OpenAI):
        self.client = client

    def _generate_prompt(self,flair: str, title: str, body: str) -> str:
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
            f"Body: {body}\n\n"
            "Respond with the best matching category and a short one-sentence justification. "
            "Respond in a JSON (OMIT MARKDOWN) in dictionary format with keys 'category' and 'reasoning'."
        )
        return prompt


    async def generate_sentiment(self, flair:Optional[str],title:str,body:Optional[str]) -> Dict[str, str]:
        """
        Asynchronously generates sentiment analysis results for a given Reddit post's flair, title, and body using an AI model.
        """
        

        if not body and not flair:
            return {} 

        prompt = self._generate_prompt(flair = flair, title = title, body = body)
        print(prompt)
        
        try:
            # acreate if the async variant 
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
                f"{self.generate_sentiment.__name__} - generate sentiment failed: {e}"
            )
            return {}


async def main():
    mod = AIModerator(client)
    result = await mod.generate_sentiment(
        flair="Discussion",
        title="How to improve my tank gameplay?",
        body="I can’t penetrate tier 8 heavy tanks…"
    )
    print(type(result))

if __name__ == "__main__":
    asyncio.run(main())