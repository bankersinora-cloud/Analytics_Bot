from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's intelligent router. Classify the user query into SQL_ONLY,
    ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    TAABI DATA CONTEXT (ONLY THESE TABLES EXIST):
    - enterprise_sites (client hubs, DCs, plants)
    - transporter_sites (partner hubs)
    - locations (lat/long/pincode)
    - geofences (entry/exit zones)
    - control_tower_vehicles (yard, reporting, movements)
    - trip_alerts (halt, overspeed, stoppages)
    - user_sites_mapping (which user sees which sites)
    - user_routes_mapping (user allowed corridor access)

    SQL_ONLY:
    - The query asks for data inside these tables.
      Examples:
        • "Show geofences of Bhiwandi"
        • "List all enterprise sites"
        • "Get vehicles inside yard right now"
        • "Show alerts in last 1 hour"
        • "Which sites user X has access to?"

    ANALYSIS_ONLY:
    - Workflow, operational process, or conceptual question.
      Examples:
        • "How does geofencing work?"
        • "What is yard reporting?"
        • "Explain overspeed alert logic"
        • "How do control tower vehicles update?"

    MIXED:
    - The query needs both data + explanation.

    Return only: SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
