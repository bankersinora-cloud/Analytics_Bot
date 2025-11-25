from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's Real-Time Tracking Router.
    Your job: classify the user's query into SQL_ONLY, ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    AVAILABLE TABLES:
    - indent_trip_tracking (gps_lat, gps_long, timestamp, speed, heading)
    - indent_trips (last_lat, last_long, last_address, status, eta)
    - indent_trips_redis_status (real-time: ignition, movement, halt_time)
    - trip_alerts (halt, overspeed, geo-deviation, unauthorized routes)
    - control_tower_vehicles (yard_status, reporting, last_mile_status)

    SQL_ONLY WHEN:
    - User asks for ANY real data:
      * "show live location of trip X"
      * "get last 10 GPS points"
      * "fetch vehicles inside yard"
      * "list overspeed alerts for last 1 hour"
      * "show redis status for this trip"
      * "get halt duration for vehicle X"
      * "show last reported address"

    ANALYSIS_ONLY WHEN:
    - User asks "how/why" explanations about tracking system:
      * "how does halt detection work?"
      * "what is unauthorized route alert?"
      * "how last_mile status gets updated?"
      * "explain tracking logic"
      * "why vehicle shows offline?"

    MIXED WHEN:
    - User asks data + explanation:
      * "show halt alerts for trip X and explain halt logic"
      * "give overspeed events and explain threshold rule"

    Output ONLY ONE WORD:
    SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
