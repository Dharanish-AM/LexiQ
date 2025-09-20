# backend/app/rag_utils.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embed_model = SentenceTransformer("all-mpnet-base-v2")

class SimpleVectorStore:
    def __init__(self):
        self.embeddings = None
        self.texts = []
        self.index = None

    def build(self, texts):
        self.texts = texts
        embs = embed_model.encode(texts, convert_to_numpy=True)
        dim = embs.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embs) # type: ignore
        self.embeddings = embs

    def query(self, q_text, k=3):
        q_emb = embed_model.encode([q_text], convert_to_numpy=True)
        D, I = self.index.search(q_emb, k) # type: ignore
        results = []
        for idx in I[0]:
            results.append(self.texts[idx])
        return results