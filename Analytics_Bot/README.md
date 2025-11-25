# TAABI Knowledge Retrieval MCP Server

This repository contains the **TAABI Knowledge Retrieval & Routing Server**, built using the `FastMCP` framework and a multi-agent architecture powered by LangChain, ChromaDB, and SentenceTransformers.

The system acts as TAABI’s **central intelligence layer**, enabling unified knowledge search, context-aware routing, and domain-specific agent execution across the entire logistics ecosystem (Indents, EPOD, Inbound, Live Trips, Analytics, Control Tower, Invoice).


## Features

### Intelligent RAG-based Query Router**
- Routes user queries to the correct domain:
  **EPOD / INBOUND / LIVE / ANALYTICS / INVOICE / INDENT / CONTROL**
- Uses MiniLM sentence embeddings + ChromaDB for semantic search.
- Enriches query context with retrieved knowledge before routing.

### Multi-Agent Architecture**
Each domain has a dedicated agent under `agents/`:

| Agent | Description |
|-------|-------------|
| analytics_agent | KPIs, dashboards, performance insights |
| control_tower_agent | Monitoring, escalations & control tower actions |
| epod_agent | EPOD processes, POD verification |
| inbound_agent | Inbound dock & shipment management |
| indent_agent | Indent creation, status, tracking |
| invoice_agent | Billing, invoice checks, cost queries |
| live_trips_agent | Real-time trip monitoring & delays |

### Conversational Memory**
- Maintains context across user interactions using LangChain’s `ConversationBufferMemory`.

### Company Knowledge Base Integration**
- Loads and processes `summary.docx`
- Splits into semantic chunks
- Stores embeddings in vector DB
- Enables contextual responses and routing


