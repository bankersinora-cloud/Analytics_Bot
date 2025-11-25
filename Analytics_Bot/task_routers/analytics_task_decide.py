from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's Analytics Routing Engine. Classify the user query into:
    SQL_ONLY, ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    ONLY THESE TABLES EXIST IN DB:
    - day_wise_summary (Daily logistics KPIs: on-time %, delay %, TAT, rejections)
    - day_wise_summary_logs (pipeline run logs)
    - day_wise_summary_raw_logs (raw aggregated info)
    - kpis (all KPI definitions, formula mapping)
    - sections (analytics dashboard left-menu groups)
    - tabs (analytics UI sub-sections)
    - user_kpi_mapping (which KPI a user is allowed to see)
    - user_kpi_config_mapping (thresholds, targets, color rules)

    SQL_ONLY WHEN:
    - User asks for numbers or analytics:
      * “Show TAT for last 7 days”
      * “Give today’s on-time %”
      * “Fetch delays by site”
      * “Which KPIs are assigned to user X”
      * “Show raw logs for yesterday”
      * “List analytics dashboard sections”

    ANALYSIS_ONLY WHEN:
    - User asks conceptual or workflow questions:
      * “How does OTIF get calculated?”
      * “Explain day_wise_summary pipeline”
      * “What is section / tab in analytics?”
      * “How does KPI threshold work?”

    MIXED WHEN:
    - User needs BOTH data + explanation:
      * “Show today’s delays and explain what causes delay KPI”
      * “Give TAT and also tell how TAT is calculated”

    Return ONLY: SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
