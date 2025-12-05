# RAG問合せ応答システム（バックエンド）

社内ドキュメントを取り込み、検索拡張生成（RAG）で回答を返す FastAPI バックエンドです。本書は要件定義書に基づき、システム構成・セットアップ・運用手順をまとめています。

## アーキテクチャ概要

```
ユーザー質問 → /query
                  │
                  ▼
         Retriever (Chroma)
                  │
                  ▼
        LLM (OpenAI GPT系)
                  │
                  ▼
    回答 + 参照メタデータ
```

- **Embedding**：`sentence-transformers`（既定 `intfloat/multilingual-e5-small`）
- **ベクトルDB**：Chroma (PersistentClient)
- **LLM**：OpenAI Chat Completions API
- **API**：FastAPI、CORS 全許可（PoC 向け）

## ディレクトリ

```
app/
 ├─ main.py              # FastAPI エントリーポイント
 ├─ config.py            # 環境設定
 ├─ document_loader.py   # PDF/TXT/MD 読み込み & チャンク化
 ├─ rag_service.py       # RAG オーケストレーション
 ├─ vector_store.py      # Chroma ラッパー
 └─ models.py            # Pydantic スキーマ
data/
 ├─ source_documents/    # 取り込み元
 └─ vector_store/        # Chroma 永続化先
```

## セットアップ

1. Python 3.10+ を用意
2. `.env` を作成
   ```bash
   cd バックエンド
   cp .env.example .env
   # OPENAI API KEY 等を追記
   ```
3. 依存ライブラリをインストール
   ```bash
   pip install -r requirements.txt
   ```
4. OpenAI API キーおよび利用モデルが利用可能であることを確認

## 起動方法

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- ヘルスチェック：`GET /health`
- ドキュメント取り込み：`POST /ingest`
- 質問回答：`POST /query`
- ファイルアップロード：`POST /documents/upload`

詳細なリクエスト/レスポンス仕様は `docs/API_SPEC.md` を参照してください。

## 運用・再取り込み

- `data/source_documents/` にファイルを配置 → `POST /ingest`（ボディ未指定で全件）
- 再 Embedding：同エンドポイントで上書き保存
- ベクトルDBをリセットしたい場合は `data/vector_store/` を空にしてから再取り込み

## テストデータ取り扱い

- PDF/TXT/Markdown (UTF-8) のみ許容
- 1 ファイル 15MB（既定値）を超えるアップロードは禁止
- 社内文書を外部転送しない要件に合わせ、アップロードはオンプレ環境内で完結

## 今後の拡張

- 認証（JWT / Azure AD 等）
- ドキュメントメタデータによるフィルタ検索
- バッチ取り込みジョブ
- 監査ログ出力
