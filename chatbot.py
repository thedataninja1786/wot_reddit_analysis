from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from typing import Optional


load_dotenv()
api_key = os.getenv("API_KEY").strip()

if not api_key:
    raise ValueError("No API key found in environment variables")

client = OpenAI(api_key=api_key)

class AIModerator:
    def __init__(self,client:OpenAI):
        self.client = client

    def _generate_prompt(self,flair: str, title: str, body: str) -> str:
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
            "Respond with the best matching category and a short one-sentence justification."
        )
        return prompt


    def generate_sentiment(self, flair:Optional[str],title:str,body:Optional[str]) -> str:
        response = ""

        if not body and not flair:
            return response 

        prompt = self._generate_prompt(flair = flair, title = title, body = body)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",
            )
            if chat_completion.choices:
                response = chat_completion.choices[0].message.content

        except Exception as e:
            print(
                f"{self.generate_sentiment.__name__} - the following exception has occurred: {e}"
            )
        finally:
            return response
