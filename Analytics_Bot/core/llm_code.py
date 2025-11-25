from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
import logging, re, json, time
from dotenv import load_dotenv
import json, os, sys, warnings

class SQLQueryCaptureHandler(BaseCallbackHandler):
    def __init__(self):
        self.queries = []

    def on_llm_end(self, response, **kwargs):
        text = response.generations[0][0].text
        if "SELECT" in text.upper():
            self.queries.append(text.strip())


def safe_run(self, query: str, *args, **kwargs):
    _original_run = QuerySQLDataBaseTool._run
    q = query.lower().strip()
    forbidden = ["insert", "update", "delete", "create", "alter",
                 "drop", "truncate", "replace", "merge"]
    if any(word in q for word in forbidden):
        raise ValueError(f"BLOCKED UNSAFE SQL: {query}")
    return _original_run(self, query, *args, **kwargs)


def build_agent(engine, allowed_tables, memory):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    QuerySQLDataBaseTool._run = safe_run
    db = SQLDatabase(engine, include_tables=allowed_tables)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=None,
        memory=memory,
        agent_type="openai-tools",
    )


def extract_sql(result):
    text_dump = json.dumps(result, ensure_ascii=False)
    matches = re.findall(r"(SELECT .*?;)", text_dump, re.IGNORECASE | re.DOTALL)
    return matches[0] if matches else "N/A"


