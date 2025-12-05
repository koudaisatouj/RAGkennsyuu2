"""Streamlit UI for the RAG問合せ応答システム backend."""

from __future__ import annotations

from typing import Dict

import requests
import streamlit as st

DEFAULT_BACKEND_URL = "http://localhost:8000"
backend_url = st.secrets.get("backend_url", DEFAULT_BACKEND_URL)

st.set_page_config(page_title="RAG問合せ応答システム", layout="wide")
st.title("RAG問合せ応答システム")
st.caption("社内ドキュメントを参照してAIが回答を作成します。")


def post_json(path: str, payload: Dict) -> requests.Response:
    url = f"{backend_url}{path}"
    return requests.post(url, json=payload, timeout=60)


def upload_file(file) -> Dict:
    url = f"{backend_url}/documents/upload"
    files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
    response = requests.post(url, files=files, timeout=120)
    response.raise_for_status()
    return response.json()


tab_query, tab_ingest = st.tabs(["質問する", "ドキュメント取り込み"])

with tab_query:
    st.subheader("質問入力")
    question = st.text_area("質問内容", placeholder="例）VPNの設定手順を教えて", height=120)
    top_k = st.slider("参照ドキュメント数", min_value=1, max_value=8, value=5)
    ask = st.button("質問する", type="primary", use_container_width=True)
    if ask:
        if not question.strip():
            st.warning("質問を入力してください。")
        else:
            try:
                response = post_json("/query", {"question": question, "top_k": top_k})
                response.raise_for_status()
                payload = response.json()
                st.success("回答を取得しました。")
                st.markdown(f"### 回答\n{payload['answer']}")
                with st.expander("参照されたコンテキストとスコア"):
                    for idx, source in enumerate(payload.get("sources", []), start=1):
                        metadata = source.get("metadata", {})
                        label = metadata.get("source", "unknown")
                        chunk_index = metadata.get("chunk_index", "?")
                        st.markdown(f"**{idx}. {label} (chunk {chunk_index})**")
                        st.write(source.get("content", ""))
                        score = source.get("score")
                        if score is not None:
                            st.caption(f"score: {score:.4f}")
                with st.expander("送信したプロンプトを確認"):
                    st.code(payload["prompt"])
            except requests.RequestException as exc:
                st.error(f"問い合わせに失敗しました: {exc}")

with tab_ingest:
    st.subheader("ファイルアップロード")
    files = st.file_uploader(
        "PDF / TXT / Markdownファイルを選択",
        type=["pdf", "txt", "md", "markdown"],
        accept_multiple_files=True,
    )
    if st.button("アップロードして取り込み", use_container_width=True):
        if not files:
            st.info("ファイルを選択してください。")
        else:
            for file in files:
                try:
                    result = upload_file(file)
                    st.success(f"{file.name}: {result['detail']}")
                except requests.RequestException as exc:
                    st.error(f"{file.name} のアップロードに失敗しました: {exc}")
    st.divider()
    st.subheader("既存ドキュメントを再取り込み")
    if st.button("全ファイルを再取り込み", use_container_width=True):
        try:
            response = post_json("/ingest", {"paths": None})
            response.raise_for_status()
            data = response.json()
            st.success(data["detail"])
        except requests.RequestException as exc:
            st.error(f"再取り込みに失敗しました: {exc}")
