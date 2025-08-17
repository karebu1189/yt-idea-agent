# yt-idea-agent
あなたのYouTube動画を収集→文字起こし→傾向分析→**企画10案**と**台本**を自動生成するGitHub Actions用エージェント。

## セットアップ
1. OpenAI APIキーを用意（`OPENAI_API_KEY`）。  
2. YouTube Data API v3 を有効化しAPIキーを取得（`YOUTUBE_API_KEY`）。  
3. GitHub Secrets に `OPENAI_API_KEY`,`YOUTUBE_API_KEY`,`CHANNEL_ID` を登録。  
4. Actions から `Run workflow`。

## 出力
- `outputs/videos.json` … 取得した動画のメタデータ＋文字起こし
- `outputs/comments.json` … 上位コメント
- `outputs/ideas.json` … 企画候補10案（JSON）
- `outputs/script.md` … 選抜1案のゆっくり解説台本
