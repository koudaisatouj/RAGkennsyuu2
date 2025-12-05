# 運用マニュアル

## 1. 日常運用

| 項目 | 内容 |
| --- | --- |
| 死活監視 | `/health` を 1 分間隔で監視 |
| ログ | `uvicorn` 標準出力を収集（例: Azure App Service ログ） |
| バックアップ | `data/vector_store` を 1 日 1 回バックアップ |
| セキュリティ | `.env` の API キーは秘密情報として管理 |

## 2. ドキュメント更新フロー

1. 新しい PDF/TXT/MD ファイルを `data/source_documents` に配置
2. `POST /ingest` を実行（body 省略で全件）
3. レスポンスの `ingested_chunks` を確認
4. `/query` でスポットテスト

## 3. アップロードAPI利用時

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@manual.pdf"
```

成功レスポンスを確認後、`POST /query` で検索精度を確認。

## 4. トラブルシューティング

| 症状 | 対応 |
| --- | --- |
| 500 OpenAI API key missing | `.env` で `RAG_OPENAI_API_KEY` を再設定後、再起動 |
| 回答が出ない | `data/vector_store` を削除 → `POST /ingest` で再構築 |
| 取り込みが遅い | `.env` で `RAG_CHUNK_SIZE` を大きくし、`sentence-transformers` モデルを軽量化 |

## 5. バージョンアップ

1. `git pull`
2. `pip install -r requirements.txt --upgrade`
3. `uvicorn` を再起動

## 6. 運用監査

- API 呼び出しログを保存し、月次でアクセス分析
- LLM プロンプト・回答は `POST /query` のレスポンス `prompt` を用いて確認
