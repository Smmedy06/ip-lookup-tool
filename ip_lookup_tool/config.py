# config.py

# --- API Keys ---
# Get your free key from https://www.abuseipdb.com/register
ABUSEIPDB_API_KEY = "64b94a5a38a75beedcf093cfdc63cc55922a0c41ecbbe27e047124c309beb40830e6eb97998dfc5c"

# Get your free key from https://ipinfo.io/signup
IPINFO_API_KEY = "4f1dfca53ad58b"

# --- Settings ---
# Order of geolocation providers to try. The system will fall back to the next one on failure.
GEO_PROVIDER_FALLBACK_ORDER = ["ipinfo", "ipapi.com"]

# Timeout in seconds for API requests
API_TIMEOUT = 10