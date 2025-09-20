# backend/app/main.py
import uvicorn, tempfile, os
from fastapi import FastAPI, UploadFile, File
from typing import List
from ocr_utils import extract_text
from nlp_utils import split_into_clauses, classify_clause_zero_shot, simplify_with_openai, detect_risk
from rag_utils import SimpleVectorStore
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
vector_store = SimpleVectorStore()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    logging.info(f"Received file upload: filename={file.filename}")
    content = await file.read()
    logging.info(f"File size: {len(content)} bytes")
    text = extract_text(content, file.filename)
    logging.info(f"Extracted text length: {len(text)}")
    clauses = split_into_clauses(text)
    logging.info(f"Number of clauses extracted: {len(clauses)}")
    # classify & simplify each clause
    out = []
    for c in clauses:
        label_res = classify_clause_zero_shot(c)
        simple = simplify_with_openai(c)
        risk = detect_risk(c)
        logging.info(f"Processed clause: label={label_res['label']}, score={label_res['score']}, simplified='{simple}', risk={risk}")
        out.append({
            "clause": c,
            "label": label_res["label"],
            "score": label_res["score"],
            "simplified": simple,
            "risk": risk
        })
    # build vector store for Q&A
    vector_store.build([c for c in clauses])
    logging.info("Built vector store with clauses")
    return {"document_text_len": len(text), "clauses": out}

@app.post("/qa")
async def qa(q: dict):
    question = q.get("question", "")
    logging.info(f"Received Q&A request: question='{question}'")
    contexts = vector_store.query(question, k=3)
    logging.info(f"Retrieved contexts: {contexts}")
    # build prompt and call OpenAI or fallback generator:
    ctx_text = "\n\n".join([f"Excerpt:\n{c}" for c in contexts])
    prompt = f"Answer the question using only the context excerpts. If unsure, say 'I don't know'.\n\n{ctx_text}\n\nQuestion: {question}\nAnswer:"
    # if OPENAI available, call it; else use local generator
    from nlp_utils import OPENAI_API_KEY, simplify_local
    if OPENAI_API_KEY:
        import openai
        resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.0) # type: ignore
        ans = resp["choices"][0]["message"]["content"].strip()
    else:
        ans = simplify_local(prompt)
    logging.info(f"Answer generated: {ans}")
    return {"answer": ans, "contexts": contexts}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)