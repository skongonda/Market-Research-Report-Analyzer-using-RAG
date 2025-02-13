import os
from dotenv import load_dotenv
import time
import openai
from openai import RateLimitError

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

def with_retry(func, max_retries=5, initial_delay=1):
    """Retry a function with exponential backoff."""
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except RateLimitError as e:
            retries += 1
            delay = initial_delay * (2 ** (retries - 1))
            print(f"Rate limit exceeded. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Max retries exceeded.")