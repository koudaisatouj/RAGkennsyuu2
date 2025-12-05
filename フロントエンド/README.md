# RAG問合せ応答システム（フロントエンド）

Streamlit で構築した簡易 UI です。FastAPI バックエンドと連携して質問/アップロードが可能です。

## セットアップ

```bash
cd フロントエンド
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

必要に応じて `.streamlit/secrets.toml` を作成し、バックエンド URL を設定します。

```toml
backend_url = "http://localhost:8000"
```

## 起動

```bash
streamlit run app.py
```

## 機能

- **質問タブ**：自由入力 → `/query` → 回答 + 参照を表示
- **ドキュメント取り込みタブ**
  - ファイルアップロード → `/documents/upload`
  - 既存ファイルの再取り込み → `/ingest`

## 注意

- 15MB を超えるファイルはアップロード不可（バックエンド設定）
- ネットワークが制限されている環境ではバックエンド URL をローカルに設定してください
