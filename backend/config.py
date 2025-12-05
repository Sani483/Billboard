import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
VIOLATION_KEYWORDS = os.getenv("VIOLATION_KEYWORDS", "nude,adult,gambling,alcohol,tobacco,drugs,weapons").split(",")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# API Configuration
API_TITLE = "Smart Billboard Compliance API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered solution for detecting unauthorized billboards"
