from openai import OpenAI
from .config import SETTINGS
import json, pathlib

client = OpenAI(api_key=SETTINGS.openai_api_key)

SYSTEM_ANALYST = """あなたはYouTube雑学・ランキング系の伸びを分析する編集者です。
過去動画の台本テキスト（文字起こし）とトップコメントを要約し、
視聴者が反応した“フック”を抽出し、次に伸びるテーマ案を10個、日本語で提案してください。
出力はJSONで: { "hooks": [...], "ideas": [{"title": "...","why":"..."}] }"""

SYSTEM_WRITER = """あなたはYouTubeの脚本家です。次の制約で台本を書いてください。
- フォーマット: ゆっくり解説風 / 導入→本編(5トピック)→まとめ
- 所要: 7〜9分想定（2200〜2600文字目安）
- トーン: 初心者にも分かりやすく、テンポ良く
- 著作権/危険行為に配慮し、具体的な出典名はぼかす"""

def analyze_and_ideate(video_summaries, comments_by_video, out_dir: pathlib.Path):
    """過去動画から傾向分析+企画10案を出し、JSON保存"""
    corpus = []
    for v in video_summaries:
        entry = {
            "video_id": v["video_id"],
            "title": v["title"],
            "published": v["published"],
            "summary": v["transcript"][:8000]  # 長すぎ防止
        }
        entry["comments"] = comments_by_video.get(v["video_id"], [])[:50]
        corpus.append(entry)

    prompt = "以下はあなたの過去動画の要約とコメントです。視聴者の嗜好とフックを抽出し、次の企画10案を。\n" + json.dumps(corpus, ensure_ascii=False)[:30000]
    rsp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role":"system","content":SYSTEM_ANALYST},
                  {"role":"user","content":prompt}],
        response_format={"type":"json_object"}
    )
    data = json.loads(rsp.choices[0].message.content)
    (out_dir / "ideas.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data

def write_script(selected_title: str, rationale: str, references: list[str], out_dir: pathlib.Path):
    user_prompt = f"""次のテーマで台本を書いてください。
タイトル: {selected_title}
狙い: {rationale}
参考（自分の過去動画の要約の抜粋/キーワード）: {json.dumps(references, ensure_ascii=False)[:4000]}"""

    rsp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role":"system","content":SYSTEM_WRITER},
                  {"role":"user","content":user_prompt}]
    )
    script = rsp.choices[0].message.content
    md = f"# {selected_title}\n\n{script}\n"
    (out_dir / "script.md").write_text(md)
    return md
