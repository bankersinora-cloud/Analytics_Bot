from core.llm_code import build_agent, SQLQueryCaptureHandler, extract_sql
from task_routers.inbound_task_decide import task_decider
from config.allowed_tables import INBOUND_TABLES
from config.db_utils import get_engine
from config.logging import create_logs
import json, os, sys, warnings, logging, time, re

engine = get_engine()

def run_inbound_agent(query, memory):
    agent = build_agent(engine, INBOUND_TABLES, memory)
    start_time = time.time()
    sql_query = "N/A"
    output = ""
    used_sql = False

    try:
        sql_capture = SQLQueryCaptureHandler()
        logger = create_logs("inbound")
        logger.info(f"USER QUERY: {query}")
        task_type = task_decider(query)
        if task_type in ["SQL_ONLY", "MIXED"]:
            try:
                result = agent.invoke({"input": query}, config={"callbacks": [sql_capture]})
                if sql_capture.queries:
                    logger.info("Generated SQL Query:")
                    logger.info(sql_capture.queries[-1])
                else:
                    logger.info("No SQL query captured.")
                used_sql = True

                sql_query = sql_capture.queries[-1] if sql_capture.queries else extract_sql(result)
                output = result.get("output", "").strip()

                if not output or output.lower() in ["none", "null", ""]:
                    raise Exception("Empty SQL output")

            except Exception:
                used_sql = False

        if not used_sql or task_type == "ANALYSIS_ONLY":

            chat_history = memory.load_memory_variables({}).get("chat_history", [])
            history = "\n".join([m.content for m in chat_history])

            analysis_prompt = f"""
            You are TAABI's Logistics Inbound Reporting Expert.

            ONLY USE THESE DOMAINS:
            - enterprise_sites (client DCs / factories)
            - transporter_sites (partner hubs)
            - geofences (entry/exit detection)
            - control_tower_vehicles (yard status, reporting, movement)
            - trip_alerts (halt, overspeed, abnormal stoppage)
            - locations (latitude, longitude, pincode)
            - user_sites_mapping (user access)
            - user_routes_mapping (route access control)

            STRICT RULES:
            - No programming answers
            - No general knowledge
            - No SQL generation here
            - Only logistics & CT operational answers

            User Question:
            {query}

            Conversation so far:
            {history}

            Provide the best operational explanation:
            """

            #output = agent.invoke(analysis_prompt).content.strip()
            response = agent.invoke(analysis_prompt)
            if isinstance(response, dict):
                output = response.get("output", "").strip()
            else:
                output = str(response).strip()

        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(output)

        time_taken = round(time.time() - start_time, 2)
        logger.info(f"RESULT: {output}...")
        logger.info(f"TIME TAKEN: {time_taken} sec")
        logger.info("-" * 80)

        return json.dumps({
            "success": True,
            "task": task_type,
            "used_sql": used_sql,
            "query": query,
            "sql": sql_query,
            "result": output,
            "time_taken_sec": time_taken
        })

    except Exception as e:
        logger.error(str(e))
        return json.dumps({
            "success": False,
            "error": str(e)
        })

