# 動作環境構築手順

## 前提

- OS: Windows/Linux/Mac (Python 3.10+)
- OpenAI API キーを取得済み
- インターネット接続（モデル/ライブラリの初回ダウンロードに利用）

## 1. リポジトリ取得

```bash
git clone <repo>
cd バックエンド
```

## 2. 仮想環境

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

## 3. 依存ライブラリ

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. 環境変数

```
cp .env.example .env
```

`.env` に以下を設定

```
RAG_OPENAI_API_KEY=sk-xxx
RAG_OPENAI_MODEL=gpt-4o-mini
RAG_EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

## 5. データディレクトリ

- `data/source_documents` に PDF/TXT/Markdown を格納
- `data/vector_store` は自動生成（既存データを削除すると再構築）

## 6. 起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 7. 動作確認

1. `POST /ingest` でドキュメント登録
2. `POST /query` で質問
3. `GET /health` でステータス確認
