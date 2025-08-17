from pydantic import BaseModel
import os, pathlib

class Settings(BaseModel):
    openai_api_key: str = os.environ["OPENAI_API_KEY"]
    youtube_api_key: str = os.environ["YOUTUBE_API_KEY"]
    channel_id: str = os.environ["CHANNEL_ID"]
    max_videos: int = int(os.environ.get("MAX_VIDEOS", 5))
    out_dir: pathlib.Path = pathlib.Path("outputs")

SETTINGS = Settings()
SETTINGS.out_dir.mkdir(parents=True, exist_ok=True)
