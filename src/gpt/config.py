import os
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_TOKEN"),
    http_client=httpx.AsyncClient(proxy='http://eAzEJHXk:6WL4egih@109.205.62.47:64856')

)

MODEL_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1000,
}