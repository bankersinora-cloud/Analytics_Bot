from core.llm_code import build_agent, SQLQueryCaptureHandler, extract_sql
from task_routers.indent_task_decide import task_decider
from config.allowed_tables import INDENT_TABLES
from config.db_utils import get_engine
from config.logging import create_logs
import json, os, sys, warnings, logging, time, re

engine = get_engine()

def run_indent_agent(query, memory):
    agent = build_agent(engine, INDENT_TABLES, memory)
    start_time = time.time()
    sql_query = "N/A"
    output = ""
    used_sql = False

    try:
        sql_capture = SQLQueryCaptureHandler()
        logger = create_logs("indent")
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
            You are TAABI's Logistics Operations Expert.

            STRICT RULES:
            - Only answer in context of logistics, transport operations, TAABI workflows,
            vehicle assignment, indent creation, trip lifecycle, transporter acceptance,
            routing, delays, fleet management.
            - Do NOT answer generic AI knowledge.
            - Do NOT give programming, math, history, or unrelated content.
            - Do NOT hallucinate new features not present in logistics operations.

            Your responsibility:
            - Explain workflows like: creating an indent, editing, cancellation,
            vehicle reporting, transporter acceptance, trip closing, LR generation,
            POD handling, delays, dispatch planning.
            - Give step-by-step instructions when user asks "How do I...?"
            - Provide clean operational reasoning when the user asks "Why/What/Which...?".
            - Never generate SQL here.
            - Keep answers practical and real-world.

            Conversation so far:
            {history}

            User question:
            {query}

            Now give the best logistics-specific operational answer:
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
