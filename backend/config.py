import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Violation Keywords
VIOLATION_KEYWORDS = os.getenv("VIOLATION_KEYWORDS", "nude,adult,gambling,alcohol,tobacco,drugs,weapons,unauthorized,prohibited").split(",")

# Frontend Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# API Configuration
API_TITLE = "Smart Billboard Compliance System"
API_VERSION = "2.0.0"
API_DESCRIPTION = "Advanced AI-powered solution for detecting unauthorized billboards with computer vision, compliance monitoring, geolocation tracking, and citizen engagement."

# Compliance & Monitoring
ZONING_DATABASE = "zoning_rules"  # Supabase table for zoning laws
COMPLIANCE_TABLE = "compliance_checks"
CITIZEN_REPORTS_TABLE = "citizen_reports"
GEOLOCATION_TABLE = "billboard_locations"

# Computer Vision Settings
OCR_CONFIDENCE_THRESHOLD = 0.5
IMAGE_RESIZE_SCALE = 2  # Scale up images for better OCR
MAX_IMAGE_SIZE_MB = 50

# Geolocation Settings
DEFAULT_COUNTRY = "US"
TIMEZONE_DEFAULT = "UTC"

# Citizen Engagement Settings
MIN_REPORTS_FOR_VALIDATION = 3  # Minimum citizen reports to auto-flag
CITIZEN_REPUTATION_THRESHOLD = 50  # Reputation points for credibility
