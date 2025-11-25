from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's EPOD Routing Engine.
    Classify the user's query into: SQL_ONLY, ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    EPOD DOMAIN (ONLY THESE TABLES EXIST):
    - trip_epod (core EPOD: timestamps, party name, receiver name, verified_by, comments)
    - trip_epod_materials (delivered_qty, dispute_qty, material details)
    - indent_trip_epod (enterprise EPOD submission)
    - indent_trips_documents_mapping (trip → document_id links)
    - trip_documents (POD images, PDFs, attachments)

    SQL_ONLY WHEN USER ASKS FOR DATA:
      • "Show EPOD for trip X"
      • "List documents for this indent"
      • "Fetch delivered qty for materials"
      • "Show disputed materials"
      • "Get EPOD timestamp"
      • "List POD files"
      • "Fetch EPOD receiver name"
      • "Show EPOD documents uploaded today"

    ANALYSIS_ONLY WHEN USER ASKS WORKFLOW / CONCEPT:
      • "How does EPOD work?"
      • "Explain partial delivery flow"
      • "What is dispute quantity?"
      • "How EPOD approval works?"
      • "Explain POD document upload flow"
      • "Why EPOD is required?"

    MIXED WHEN BOTH ARE REQUIRED:
      • "Show epod of trip X and explain what dispute qty means"
      • "Fetch documents and also explain EPOD workflow"

    RETURN ONLY ONE WORD:
    SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
