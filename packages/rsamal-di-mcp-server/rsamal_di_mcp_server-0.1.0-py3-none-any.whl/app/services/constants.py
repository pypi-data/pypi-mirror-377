"""
Central constants for all services.
All service-specific endpoints and IDs live here.
"""

# ---- Policy Service Endpoints ----
RULE_LHS_TERMS_PATH = "/v3/enforcement/terms/LHS?lhs_version=LHS_45"

# ---- Search Endpoints ----
SEARCH_PATH = "/v3/search"

# ---- service/tools specific endpoints go here ----
ASSISTANT_BASE_ENDPOINT = "/semantic_automation/v1/assistant"
LINEAGE_BASE_ENDPOINT = "/gov_lineage/v2"
TEXT_TO_SQL_BASE_ENDPOINT = "/semantic_automation/v1/text_to_sql"

CLOUD_IAM_ENDPOINT = "/identity/token"
CPD_IAM_ENDPOINT = "/icp4d-api/v1/authorize"

JSON_CONTENT_TYPE = "application/json"
JSON_PATCH_CONTENT_TYPE = "application/json-patch+json"