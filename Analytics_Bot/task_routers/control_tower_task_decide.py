from langchain_openai import ChatOpenAI

def task_decider(query):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    decision_prompt = f"""
    You are TAABI's Alerts & Notification Routing Engine.
    Your job is to classify the user query as SQL_ONLY, ANALYSIS_ONLY, or MIXED.

    USER QUERY:
    "{query}"

    AVAILABLE DATA DOMAIN:
    --------------------------------------
    ALERT META:
      - alert_types (halt alert, overspeed alert, breakdown, deviation)
      - alert_channels (SMS, Email, WhatsApp, Push)
      - alert_type_channel_mapping (which alert supports which channel)

    ALERT CONFIGURATION:
      - alert_configurations (thresholds: halt mins, overspeed kmph, deviation km)
      - alert_configuration_role_mapping (who is allowed to receive)
      - alert_configuration_role_channel_mapping (role → channel mapping)

    ALERT DATA:
      - alert_logs (all triggered alerts with timestamps)
      - alert_redis_backup (real-time alert state)

    CONTROL TOWER:
      - control_tower_indents (real-time indent stage workflow)
      - control_tower_vehicles (SLA monitoring: yard, reporting, last-mile)

    NOTIFICATION ENGINE:
      - noti_queues (pending notifications)
      - sms_queues, sms_templates, sms_logs
      - email_queues, email_templates, email_logs

    --------------------------------------

    WHEN TO CHOOSE SQL_ONLY:
      - User asks for actual data from tables.
      Examples:
        • "Show halt alerts in last 1 hour"
        • "List all alert types"
        • "Get configuration for overspeed"
        • "Fetch pending items in noti_queue"
        • "Show SMS logs for trip X"
        • "Which channels are mapped to halt alert?"
        • "Show email templates"

    WHEN TO CHOOSE ANALYSIS_ONLY:
      - User asks HOW/WHY/WHAT about alerts or notifications.
      Examples:
        • "How does alert configuration work?"
        • "What is alert channel mapping?"
        • "How CT indent stages work?"
        • "Explain SMS queue retry logic"
        • "Why alerts fail sometimes?"

    WHEN TO CHOOSE MIXED:
      - User wants both explanation + data.
      Examples:
        • "Show halt alerts and explain halt logic"
        • "Fetch SMS templates and explain how SMS triggering works"

    Return ONLY ONE WORD:
      SQL_ONLY / ANALYSIS_ONLY / MIXED
    """
    return llm.invoke(decision_prompt).content.strip().upper()
