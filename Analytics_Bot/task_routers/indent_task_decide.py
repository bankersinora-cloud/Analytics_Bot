from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's intelligent router. Your job is to classify the user's query
    into the correct task type based on whether the question requires database data,
    operational workflow knowledge, or both.

    USER QUERY:
    "{query}"

    CLASSIFICATION RULES:
    ---------------------------------------------------------------
    1. SQL_ONLY  → Choose this ONLY if:
       - The user is asking for data stored inside the database.
       - Queries that include: show, list, find, get, fetch, count, last, summary, 
         pending, completed, accepted, rejected, trips, indents, vehicles, routes,
         transporter performance, delays, trends, history, reporting times.
       - Anything requiring filtering, grouping, time range, status, drill-down.
       - If the answer depends on actual DB rows → ALWAYS SQL_ONLY.

    2. ANALYSIS_ONLY → Choose this ONLY if:
       - The user is asking "How to do something?" (workflows)
         e.g., “How do I create an indent?”, “How to cancel a trip?”
       - The user is asking operational reasoning:
         “Why is a trip delayed?”, “What happens after reporting?”,
         “Explain transporter acceptance flow”.
       - The user is NOT asking for any specific data.
       - The answer is procedural, conceptual, or explanatory.

    3. MIXED → Choose this when:
       - The user asks a data question PLUS explanation.
       - Example:
         “Show me delayed trips and also explain why delays happen.”
         “List rejected indents and guide how to reduce rejection.”

    IMPORTANT CONSTRAINTS:
    - If the query contains ANY numeric/time filter (today, last 7 days, count, etc.)
      → lean towards SQL_ONLY unless explicitly asking for explanation.
    - If the query contains verbs like "show", "list", "find", “pull”, “fetch”
      → ALWAYS SQL_ONLY.
    - If the query contains "how", "why", "explain", "steps", "process"
      → MOST LIKELY ANALYSIS_ONLY (unless data is requested).

    Return ONLY ONE WORD:
    SQL_ONLY / ANALYSIS_ONLY / MIXED
    ---------------------------------------------------------------
    """
    return llm.invoke(decision_prompt).content.strip().upper()
