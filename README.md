# RAG問合せ応答システム

社内ドキュメントを活用し、RAG（検索拡張生成）で質問に回答するシステムです。  
バックエンドは FastAPI、フロントエンドは Streamlit を使用しています。

## 1. プロジェクト構成

```
RAG研修/
├─ バックエンド/        # FastAPI アプリケーション
│   ├─ app/            # API・サービス実装
│   ├─ data/           # ドキュメント・ベクトルDB
│   ├─ docs/           # API仕様書・セットアップ手順など
│   └─ requirements.txt
├─ フロントエンド/      # Streamlit UI
│   ├─ app.py
│   ├─ README.md
│   ├─ requirements.txt
│   └─ .streamlit/     # secrets 設定
└─ README.md           # 本ファイル
```

## 2. 前提条件

- Python 3.11 以上
- OpenAI API キーを取得済み（`.env` に設定）
- Windows 端末を想定した PowerShell 手順

## 3. バックエンドのセットアップ

```powershell
cd バックエンド
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # OpenAI キーなどを編集
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

主なエンドポイント：

- `GET /health` … ヘルスチェック
- `POST /ingest` … ドキュメント取り込み
- `POST /query` … 質問受付
- `POST /documents/upload` … ファイルアップロード + 取り込み
- `GET /docs` … Swagger UI

## 4. フロントエンドのセットアップ

```powershell
cd フロントエンド
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# backend_url を変更したい場合は .streamlit/secrets.toml を編集
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開くと UI が表示され、質問タブ / ドキュメント取り込みタブから API を利用できます。

## 5. ドキュメント取り込み

1. `バックエンド/data/source_documents/` に PDF/TXT/Markdown ファイルを配置（UTF-8 推奨）。
2. `POST /ingest` もしくは Streamlit の「全ファイルを再取り込み」でベクトル化。
3. ベクトルDB (`data/vector_store/`) に永続化されます。

## 6. 注意点

- OpenAI API キーは `.env` にのみ保存し、リポジトリにコミットしないでください。
- Streamlit の `backend_url` は `secrets.toml` で管理しています。環境に応じて変更してください。
- 取り込み対象ファイルは 15MB を超えないようにしてください（`.env` で変更可）。

## 7. 参考資料

- 詳細な API 仕様: `バックエンド/docs/API_SPEC.md`
- セットアップ手順: `バックエンド/docs/SETUP.md`
- 運用手順: `バックエンド/docs/OPERATIONS.md`

これらを参照し、社内 FAQ やマニュアルの検索・回答支援にご活用ください。
