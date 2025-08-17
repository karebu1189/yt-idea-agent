from .config import SETTINGS
from . import youtube as yt
from . import transcribe
from . import analyze
import pathlib, json, traceback

def main():
    out = SETTINGS.out_dir
    videos = yt.get_latest_videos()
    enriched = []
    comments_by_video = {}

    for v in videos:
        print(f"[Video] {v['title']} ({v['url']})")
        text = yt.try_fetch_transcript(v["video_id"])
        if text is None:
            print(" - 字幕なし → 音声DL→文字起こし")
            audio = yt.download_audio_with_ytdlp(v["url"])
            text = transcribe.transcribe_file(audio)
        v["transcript"] = text
        enriched.append(v)

        try:
            comments = yt.fetch_top_comments(v["video_id"], max_comments=50)
        except Exception:
            comments = []
        comments_by_video[v["video_id"]] = comments

    # 保存（生データ）
    (out / "videos.json").write_text(json.dumps(enriched, ensure_ascii=False, indent=2))
    (out / "comments.json").write_text(json.dumps(comments_by_video, ensure_ascii=False, indent=2))

    # 分析→企画10案
    ideas = analyze.analyze_and_ideate(enriched, comments_by_video, out)

    # 一番良さそうな案を選んで台本作成（とりあえず先頭）
    top = ideas["ideas"][0]
    refs = [v["title"] for v in enriched]
    analyze.write_script(top["title"], top.get("why",""), refs, out)

    print("✅ 完了: outputs/ideas.json / outputs/script.md / outputs/*.json")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        raise
