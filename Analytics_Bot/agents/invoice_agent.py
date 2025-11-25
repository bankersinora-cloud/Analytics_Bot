from core.llm_code import build_agent, SQLQueryCaptureHandler, extract_sql
from task_routers.invoice_task_decide import task_decider
from config.allowed_tables import INVOICE_TABLES
from config.db_utils import get_engine
from config.logging import create_logs
import json, os, sys, warnings, logging, time, re

engine = get_engine()

def run_invoice_agent(query, memory):
    agent = build_agent(engine, INVOICE_TABLES, memory)
    start_time = time.time()
    sql_query = "N/A"
    output = ""
    used_sql = False

    try:
        sql_capture = SQLQueryCaptureHandler()
        logger = create_logs("invoice")
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
            You are TAABI's Logistics Freight, Billing & Contract Charges Expert.

            YOU MUST ANSWER USING ONLY THIS DOMAIN:
              - trip_freight_invoice (final invoice logic)
              - trip_goods_invoice (invoice summary)
              - trip_goods_invoice_materials (material-level billing)
              - contract_freight_charges (base freight logic)
              - contract_late_delivery_penalty_charge
              - contract_late_reporting_at_origin_charge
              - contract_loading_unloading_charges
              - contract_detention_charges
              - mst_loading_charges / mst_unloading_charges
              - mst_late_delivery_charges (default slabs)

            STRICT RULES:
              - Do NOT generate SQL here
              - Do NOT answer programming or generic questions
              - ONLY explain billing, penalties, freight logic, contract rules

            USER QUESTION:
            {query}

            Conversation so far:
            {history}

            Provide the correct freight/billing operational explanation:
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