ANALYTICS_TABLES = [
    "day_wise_summary",
    "day_wise_summary_logs",
    "day_wise_summary_raw_logs",
    "kpis",
    "sections",
    "tabs",
    "user_kpi_mapping",
    "user_kpi_config_mapping"
]

CONTROL_TOWER_TABLES = [
    "alert_types",
    "alert_channels",
    "alert_type_channel_mapping",
    "alert_configurations",
    "alert_configuration_role_mapping",
    "alert_configuration_role_channel_mapping",
    "alert_logs",
    "alert_redis_backup",
    "control_tower_indents",
    "control_tower_vehicles",
    "noti_queues",
    "sms_queues",
    "sms_templates",
    "sms_logs",
    "email_queues",
    "email_templates",
    "email_logs"
]

EPOD_TABLES = [
    "trip_epod",                       
    "trip_epod_materials",             
    "indent_trip_epod",                
    "indent_trips_documents_mapping",  
    "trip_documents"                   
]

INBOUND_TABLES = [
    "enterprise_sites",
    "transporter_sites",
    "locations",
    "geofences",
    "control_tower_vehicles",
    "trip_alerts",
    "user_sites_mapping",
    "user_routes_mapping"
]

INDENT_TABLES = [
    "indents",
    "indent_load_types",
    "indent_rejected_vehicle",
    "indent_stoppages",
    "indent_transporter_mapping",
    "indent_transporter_accepted_qty",
    "indent_trips",
    "indent_trip_charges",
    "indent_trip_elr",
    "indent_trip_elr_products",
    "indent_trip_epod",
    "indent_trip_tracking",
    "indent_trip_removed_vehicles",
    "indent_trips_redis_status",
    "indent_trips_documents_mapping",
    "indent_vehicle_mapping",
    "mst_routes",
    "mst_routes_stoppages",
    "mst_vehicle_master",
    "mst_vehicle_types"
]

INVOICE_TABLES = [
    "trip_freight_invoice",
    "trip_goods_invoice",
    "trip_goods_invoice_materials",
    "contract_freight_charges",
    "contract_late_delivery_penalty_charge",
    "contract_late_reporting_at_origin_charge",
    "contract_loading_unloading_charges",
    "contract_detention_charges",
    "mst_loading_charges",
    "mst_unloading_charges",
    "mst_late_delivery_charges"
]

LIVE_TRIPS_TABLES = [
    "indent_trip_tracking",          
    "indent_trips",                  
    "indent_trips_redis_status",     
    "trip_alerts",                  
    "control_tower_vehicles"         
]