# API仕様書

## 共通

- Base URL: `http://<host>:8000`
- Header: `Content-Type: application/json`（アップロード時を除く）
- 認証: なし（PoC 想定）

## 1. ヘルスチェック

- **Method**: `GET /health`
- **Response**
  ```jsonc
  {
    "status": "ok",
    "environment": "development"
  }
  ```

## 2. ドキュメント取り込み

- **Method**: `POST /ingest`
- **Body**
  ```jsonc
  {
    "paths": [
      "manuals/vpn_guide.pdf",
      "faq/network.md"
    ]
  }
  ```
  - `paths` を省略すると `data/source_documents` 以下の全ファイルが対象

- **Response**
  ```jsonc
  {
    "ingested_files": 2,
    "ingested_chunks": 42,
    "skipped_files": 0,
    "detail": "42 chunks stored from 2 files."
  }
  ```

## 3. 質問受付

- **Method**: `POST /query`
- **Body**
  ```jsonc
  {
    "question": "VPNの設定手順は？",
    "top_k": 5
  }
  ```
- **Response**
  ```jsonc
  {
    "question": "VPNの設定手順は？",
    "answer": "VPNクライアントを起動し…",
    "prompt": "You are an AI assistant ...",
    "sources": [
      {
        "id": "8e828e...",
        "content": "VPN クライアントのインストール手順...",
        "metadata": {
          "source": "vpn_manual.pdf",
          "path": "/data/source_documents/vpn_manual.pdf",
          "chunk_index": "0"
        },
        "score": 0.11
      }
    ]
  }
  ```
- **エラー**
  - `400`: 質問未入力
  - `500`: OpenAI API キー未設定など

## 4. ファイルアップロード + 取り込み

- **Method**: `POST /documents/upload`
- **Header**: `Content-Type: multipart/form-data`
- **Form Data**
  - `file`: PDF/TXT/Markdown
- **Response**
  ```jsonc
  {
    "ingested_files": 1,
    "ingested_chunks": 10,
    "skipped_files": 0,
    "detail": "Uploaded vpn_manual.pdf and stored 10 chunks."
  }
  ```
- **制約**
  - ファイルサイズ <= 15MB（`.env` で変更可）
  - 拡張子: `.pdf`, `.txt`, `.md`, `.markdown`
