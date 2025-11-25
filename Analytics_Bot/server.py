from mcp.server.fastmcp import FastMCP
from agents.analytics_agent import run_analytics_agent
from agents.control_tower_agent import run_control_tower_agent
from agents.epod_agent import run_epod_agent
from agents.inbound_agent import run_inbound_agent
from agents.indent_agent import run_indent_agent
from agents.invoice_agent import run_invoice_agent
from agents.live_trips_agent import run_live_trips_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
#from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
#from langchain_community.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
import docx2txt
import sys, os, json

mcp = FastMCP("taabi-server")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def load_doc(path):
    text = docx2txt.process(path)
    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])

def make_chunks(text, size=2500):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])


knowledge_text = load_doc("summary.docx")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_text(knowledge_text)
db = Chroma.from_texts(chunks, embeddings)


def rag_route(query: str):
    prompt_template = """
    You are TAABI Intelligent Query Router.

    ROUTE QUERY BASED ON CONTEXT & INTELLIGENCE.
    Respond strictly in one word.

    CONTEXT:
    {context}

    QUERY:
    {query}

    Allowed:
    EPOD / INBOUND / LIVE / ANALYTICS / INVOICE / INDENT / CONTROL
    """

    prompt = PromptTemplate(
        input_variables=["context", "query"],
        template=prompt_template,
    )
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    chain = RunnableSequence(prompt, llm)
    docs = db.similarity_search(query, k=5)
    context = "\n".join([d.page_content for d in docs])

    response = chain.invoke({"context": context, "query": query})
    result = response.content.strip().upper()
    return result #llm.invoke(routing_prompt).content.strip().upper()

@mcp.tool()
def ask_taabi(query: str) -> str:
    route = rag_route(query)

    if route == "EPOD":
        return str(run_epod_agent(query, memory))
    if route == "ANALYTICS":
        return str(run_analytics_agent(query, memory))
    if route == "CONTROL":
        return str(run_control_tower_agent(query, memory))
    if route == "INVOICE":
        return str(run_invoice_agent(query, memory))
    if route == "INDENT":
        return str(run_indent_agent(query, memory))
    if route == "INBOUND":
        return str(run_inbound_agent(query, memory))
    if route == "LIVE":
        return str(run_live_trips_agent(query, memory))

    return json.dumps({"success": False, "error": "Route not found"})

if __name__ == "__main__":
    print("Starting TAABI MCP Server...", file=sys.stderr)
    mcp.run()
