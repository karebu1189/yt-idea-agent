from openai import OpenAI
from .config import SETTINGS
import pathlib

client = OpenAI(api_key=SETTINGS.openai_api_key)

def transcribe_file(path: str) -> str:
    """
    OpenAIの音声APIで文字起こし。
    推奨: gpt-4o-transcribe（Whisper後継の高精度モデル）
    """
    with open(path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            response_format="text"
        )
    return tr  # 返り値はテキスト
