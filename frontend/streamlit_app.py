# frontend/streamlit_app.py
import streamlit as st # type: ignore
import requests
import json

import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("⚖️ LexiQ — Demystify Legal Contracts")

uploaded = st.file_uploader("Upload PDF/DOCX", type=["pdf","docx"])
if uploaded:
    with st.spinner("Uploading and analyzing..."):
        files = {"file": (uploaded.name, uploaded.read(), uploaded.type)}
        r = requests.post(f"{API_URL}/upload", files=files, timeout=120)
    if r.status_code == 200:
        data = r.json()
        st.success("Analysis complete")
        for i, c in enumerate(data["clauses"]):
            with st.expander(f"Clause {i+1} — {c['label']} (score {c['score']:.2f})"):
                st.markdown("**Original:**")
                st.write(c["clause"])
                st.markdown("**Simplified:**")
                st.write(c["simplified"])
                st.markdown("**Risk:**")
                st.write(c["risk"])
    else:
        st.error("Analysis failed: " + r.text)

st.header("Ask a question about the document")
question = st.text_input("Question (e.g., What are my termination rights?)")
if st.button("Ask") and question:
    r = requests.post(f"{API_URL}/qa", json={"question": question})
    if r.status_code == 200:
        out = r.json()
        st.markdown("**Answer (grounded):**")
        st.write(out["answer"])
        st.markdown("**Used contexts:**")
        for ctx in out["contexts"]:
            st.write(ctx)
    else:
        st.error("Q&A failed")