# backend/app/nlp_utils.py
import re
import spacy
from transformers import pipeline
from config import CLASSES, MAX_CLAUSE_LENGTH, OPENAI_API_KEY
import openai

nlp = spacy.load("en_core_web_sm")

# Zero-shot classifier (quick for hackathon)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
# optionally: generator for local simplification
generator = pipeline("text2text-generation", model="google/flan-t5-small")

# OpenAI init (if key available)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def split_into_clauses(text):
    # heuristic: split on double newline or on headings like "Section X." or long sentences
    parts = re.split(r'\n{2,}|\r\n{2,}', text)
    # further break very long parts into sentences
    clauses = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > MAX_CLAUSE_LENGTH:
            doc = nlp(p)
            for sent in doc.sents:
                s = sent.text.strip()
                if len(s) > 20:
                    clauses.append(s)
        else:
            clauses.append(p)
    return clauses

def classify_clause_zero_shot(clause_text):
    # returns the best label and scores
    res = classifier(clause_text, candidate_labels=CLASSES, multi_label=False)
    return {"label": res["labels"][0], "score": float(res["scores"][0])} # type: ignore

def simplify_with_openai(clause_text):
    if not OPENAI_API_KEY:
        return simplify_local(clause_text)
    prompt = f"You are a plain-English legal explainer. Rewrite this clause in simple language (grade 8), keep it short, and list any obligations or deadlines.\n\nClause:\n{clause_text}\n\nOutput (simple explanation + obligations):"
    resp = openai.ChatCompletion.create( # type: ignore
        model="gpt-4o-mini", # or gpt-4 if available
        messages=[{"role":"user","content":prompt}],
        max_tokens=400,
        temperature=0.2
    )
    return resp["choices"][0]["message"]["content"].strip()

def simplify_local(clause_text):
    # fallback using small flan-t5
    prompt = f"Simplify this legal clause into simple English and list obligations:\n\n{clause_text}"
    out = generator(prompt, max_length=120)[0]["generated_text"]
    return out

risk_keywords = ["indemnity","liabilit","penalty","terminate","auto renew","automatic renewal","breach","forfeit","damages"]
def detect_risk(clause_text):
    score = 0
    reasons = []
    lc = clause_text.lower()
    for kw in risk_keywords:
        if kw in lc:
            score += 1
            reasons.append(kw)
    severity = "low"
    if score >= 3:
        severity = "high"
    elif score == 2:
        severity = "medium"
    return {"severity": severity, "matches": reasons}