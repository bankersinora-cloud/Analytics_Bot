from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's Freight & Billing Router.
    Classify the user query into: SQL_ONLY, ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    FREIGHT / BILLING TABLES (ONLY THESE EXIST):
    ---------------------------------------------------------
    trip_freight_invoice:
      - final freight amount, extra charges, deductions, taxes

    trip_goods_invoice:
      - goods invoice summary

    trip_goods_invoice_materials:
      - material-level invoice amounts, delivered qty billing,
        short/excess qty adjustments

    contract_freight_charges:
      - base freight, per-km/per-ton/per-case rules

    contract_late_delivery_penalty_charge:
      - late delivery fines (SLA delay penalties)

    contract_late_reporting_at_origin_charge:
      - late reporting charges at loading point

    contract_loading_unloading_charges:
      - loading/unloading cost rules

    contract_detention_charges:
      - detention charges (free hours, rate per hour)

    mst_loading_charges, mst_unloading_charges, mst_late_delivery_charges:
      - master data for charge slabs and default values
    ---------------------------------------------------------

    SQL_ONLY WHEN user asks:
      • "Show freight invoice for trip X"
      • "Fetch detention charges"
      • "List materials in goods invoice"
      • "Get late delivery penalties"
      • "Show contract freight rate"
      • "Fetch trip charges summary"
      • "Show unloading charge rules"

    ANALYSIS_ONLY WHEN user asks:
      • "How is freight calculated?"
      • "Explain detention calculation"
      • "How late delivery penalty works?"
      • "What is per-ton billing?"
      • "How contract slabs are applied?"
      • "Explain billing workflow"

    MIXED WHEN both data + explanation required:
      • "Show freight invoice and explain calculation"
      • "Fetch penalty and tell how penalty works"

    RETURN ONLY ONE WORD:
    SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
