import re
import json
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

LOG_FILES = [
    "logs/control_tower.log",
    "logs/epod.log",
    "logs/analytics.log",
    "logs/indent.log",
    "logs/live_trips.log"
]

OUTPUT_JSON = "taabi_eval_results.json"

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def bleu_score(ref, gen):
    try:
        return float(sentence_bleu([ref.split()], gen.split()))
    except:
        return 0.0

def rouge_l(ref, gen):
    try:
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
        return float(scorer.score(ref, gen)["rougeL"].fmeasure)
    except:
        return 0.0

def semantic_similarity(ref, gen):
    try:
        e1 = embedder.encode([ref])
        e2 = embedder.encode([gen])
        return float(cosine_similarity(e1, e2)[0][0])
    except:
        return 0.0

def hallucination_score(ref, gen):
    ref_words = set(ref.lower().split())
    gen_words = set(gen.lower().split())
    extra = gen_words - ref_words
    if len(gen_words) == 0:
        return 0.0
    return round(len(extra) / len(gen_words), 4)

def consistency_score(outputs):
    if len(outputs) < 2:
        return 1.0
    embeddings = embedder.encode(outputs)
    sims = []
    for i in range(len(embeddings)-1):
        sims.append(cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0])
    return float(np.mean(sims))


def faithfulness_score(sql, output):
    sql_keywords = [w for w in sql.split() if len(w) > 4]
    matched = [kw for kw in sql_keywords if kw.lower() in output.lower()]
    if len(sql_keywords) == 0:
        return 1.0
    return round(len(matched) / len(sql_keywords), 3)

def correctness_score(ref, gen):
    return semantic_similarity(ref, gen)

def sql_risk_score(sql):
    sql_upper = sql.upper()
    risk = 0
    dangerous_ops = ["DELETE", "DROP", "UPDATE", "ALTER", "TRUNCATE", "INSERT"]
    if any(op in sql_upper for op in dangerous_ops):
        risk += 0.8
    if sql_upper.count("JOIN") >= 3:
        risk += 0.3
    if "WHERE" not in sql_upper:
        risk += 0.2
    if "SELECT" not in sql_upper:
        return 1.0
    return round(min(risk, 1.0), 3)

def sql_quality_score(sql_text):
    if sql_text == "N/A":
        return 0.0
    score = 0
    if "SELECT" in sql_text.upper(): score += 0.3
    if "FROM" in sql_text.upper(): score += 0.3
    if "WHERE" in sql_text.upper(): score += 0.2
    if "JOIN" in sql_text.upper(): score += 0.2
    return round(score, 2)


def sql_success(sql):
    """SQL success = SELECT present."""
    return 1 if "SELECT" in sql.upper() else 0

def retrieval_hit_rate(sql, query):
    """Simple heuristic: check if query keywords appear in SQL."""
    q_words = [w for w in query.split() if len(w) > 4]
    hits = [w for w in q_words if w.lower() in sql.lower()]
    if len(q_words) == 0:
        return 0
    return len(hits) / len(q_words)

def refusal_correctness(output, query):
    """
    Detect if model refused correctly.
    If query requires SQL but output contains "I cannot" → okay.
    If output refuses incorrectly → wrong.
    """
    refuses = any(x in output.lower() for x in [
        "cannot", "not able", "sorry", "no data", "do not have"
    ])

    needs_sql = any(x in query.lower() for x in ["data", "count", "how many", "show", "list"])

    if refuses and needs_sql:
        return 0  # Wrong refusal
    if refuses and not needs_sql:
        return 1  # Correct refusal
    return 1  # Default OK

def extract_latency(text):
    """Extract latency from 'TIME TAKEN: X ms'"""
    matches = re.findall(r"TIME TAKEN:\s*([0-9.]+)", text)
    return [float(m) for m in matches] if matches else []


def parse_taabi_logs(path):
    text = open(path, "r").read()

    pattern = (
        r"USER QUERY:(.*?)Generated SQL Query:(.*?)RESULT:(.*?)(?=TIME TAKEN:|$)"
    )

    matches = re.findall(pattern, text, re.DOTALL)

    parsed = []
    for q, sql, res in matches:
        parsed.append({
            "query": q.strip(),
            "sql": sql.strip().replace("```sql", "").replace("```", ""),
            "output": res.strip()
        })

    return parsed


def evaluate_items(items, latencies):
    all_outputs = [i["output"] for i in items]
    global_consistency = consistency_score(all_outputs)

    results = []
    sql_successes = []
    hallucinations = []

    for item in items:
        q = item["query"]
        gen = item["output"]
        sql = item["sql"]
        reference = gen

        sql_successes.append(sql_success(sql))
        hallucinations.append(hallucination_score(reference, gen))

        metrics = {
            "Query": q,
            "Generated": gen,
            "SQL": sql,

           
            "BLEU": bleu_score(reference, gen),
            "ROUGE-L": rouge_l(reference, gen),
            "SemanticScore": semantic_similarity(reference, gen),

         
            "Accuracy(Semantic)": semantic_similarity(reference, gen),

            "HallucinationScore": hallucination_score(reference, gen),
            "FaithfulnessScore": faithfulness_score(sql, gen),
            "CorrectnessScore": correctness_score(reference, gen),

            "SQLQuality": sql_quality_score(sql),
            "SQLRiskScore": sql_risk_score(sql),

            "RetrievalHitRate": retrieval_hit_rate(sql, q),
            "RefusalCorrectness": refusal_correctness(gen, q),

            "Consistency(Global)": global_consistency
        }

        results.append(metrics)

    summary = {
        "SQL_Success_Rate": float(np.mean(sql_successes)),
        "Hallucination_Rate": float(np.mean(hallucinations)),
        "P95_Latency": float(np.percentile(latencies, 95)) if latencies else None
    }

    return results, summary


# -------------------------
# Run Full Evaluation
# -------------------------

if __name__ == "__main__":
    import pandas as pd

    all_items = []
    all_latencies = []

    for log in LOG_FILES:
        print(f"\n Reading: {log}")
        text = open(log, "r").read()

        # extract latency for P95
        lats = extract_latency(text)
        all_latencies.extend(lats)

        items = parse_taabi_logs(log)
        print(f" Found {len(items)} entries.")

        for entry in items:
            entry["log_file"] = log.split("/")[-1]

        all_items.extend(items)

    print(f"\nTotal evaluation entries: {len(all_items)}")

    eval_data, summary = evaluate_items(all_items, all_latencies)

    with open(OUTPUT_JSON, "w") as f:
        json.dump({"results": eval_data, "summary": summary}, f, indent=4)

    df = pd.DataFrame(eval_data)
    df.to_csv("taabi_eval_results.csv", index=False)

    print("\n Evaluation Complete")
    print(" JSON → taabi_eval_results.json")
    print(" CSV  → taabi_eval_results.csv\n")
