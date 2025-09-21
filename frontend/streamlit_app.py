# frontend/streamlit_app.py
import streamlit as st  # type: ignore
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="LexiQ — Demystify Legal Contracts", layout="wide")

st.title("⚖️ LexiQ — Demystify Legal Contracts")

# Upload Section
uploaded = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"])

clauses_data = None

if uploaded:
    with st.spinner("Uploading and analyzing..."):
        files = {"file": (uploaded.name, uploaded.read(), uploaded.type)}
        r = requests.post(f"{API_URL}/upload", files=files, timeout=120)

    if r.status_code == 200:
        clauses_data = r.json()
        st.success("Analysis complete")
    else:
        st.error("Analysis failed: " + r.text)

# Sidebar — Display Clauses
if clauses_data:
    st.sidebar.header("📑 Clauses Overview")
    for i, c in enumerate(clauses_data["clauses"]):
        with st.sidebar.expander(f"Clause {i+1} — {c['label']} (score {c['score']:.2f})"):
            st.markdown("**Original:**")
            st.write(c["clause"])
            st.markdown("**Simplified:**")
            st.write(c["simplified"])
            st.markdown("**Risk:**")
            st.write(c["risk"])

# Q&A Section
st.header("💬 Ask a question about the document")
question = st.text_input("Question (e.g., What are my termination rights?)")

if st.button("Ask") and question:
    r = requests.post(f"{API_URL}/qa", json={"question": question})
    if r.status_code == 200:
        out = r.json()
        st.markdown("**Answer (grounded):**")
        st.write(out["answer"])

        st.markdown("**📌 Used contexts:**")
        for ctx in out["contexts"]:
            st.write(ctx)
    else:
        st.error("Q&A failed")
