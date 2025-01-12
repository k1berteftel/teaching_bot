from openai import AsyncOpenAI
from os import getenv
from dotenv import load_dotenv
import httpx
load_dotenv()

client = AsyncOpenAI(
    api_key=getenv("OPENAI_TOKEN"),
    http_client=httpx.AsyncClient(proxy='http://eAzEJHXk:6WL4egih@109.205.62.47:64856')
)
