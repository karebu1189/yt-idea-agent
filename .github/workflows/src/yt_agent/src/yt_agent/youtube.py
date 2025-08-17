from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from typing import List, Dict, Optional
import subprocess, json, tempfile, os
from .config import SETTINGS

def get_latest_videos() -> List[Dict]:
    """チャンネルの最新動画（ID/タイトル/公開日/URL）を取得"""
    yt = build("youtube", "v3", developerKey=SETTINGS.youtube_api_key)
    # uploadsプレイリストを辿る
    ch = yt.channels().list(part="contentDetails", id=SETTINGS.channel_id).execute()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = yt.playlistItems().list(part="contentDetails,snippet", playlistId=uploads, maxResults=SETTINGS.max_videos).execute()
    videos = []
    for it in pl["items"]:
        vid = it["contentDetails"]["videoId"]
        title = it["snippet"]["title"]
        published = it["contentDetails"]["videoPublishedAt"]
        videos.append({"video_id": vid, "title": title, "published": published, "url": f"https://www.youtube.com/watch?v={vid}"})
    return videos

def try_fetch_transcript(video_id: str, lang_priority=("ja", "en")) -> Optional[str]:
    """字幕APIで取得。なければ None"""
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        for pref in lang_priority:
            if transcripts.find_transcript([pref]):
                t = transcripts.find_transcript([pref]).fetch()
                return " ".join([x["text"] for x in t])
    except (TranscriptsDisabled, NoTranscriptFound, Exception):
        return None
    return None

def download_audio_with_ytdlp(video_url: str) -> str:
    """yt-dlpで音声をm4aに保存してパスを返す（ffmpeg 必須）"""
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
    out.close()
    # bestaudio→m4a に変換
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "m4a",
        "-o", out.name,
        video_url
    ]
    subprocess.check_call(cmd)
    return out.name

def fetch_top_comments(video_id: str, max_comments=50) -> List[str]:
    yt = build("youtube", "v3", developerKey=SETTINGS.youtube_api_key)
    req = yt.commentThreads().list(part="snippet", videoId=video_id, maxResults=min(100, max_comments), order="relevance", textFormat="plainText")
    res = req.execute()
    comments = []
    for it in res.get("items", []):
        comments.append(it["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
    return comments
