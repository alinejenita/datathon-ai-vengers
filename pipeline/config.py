import os
from dotenv import load_dotenv

load_dotenv()

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "324b307cd319eb92fb5e2b39fe6bda43")

# Amazon SP-API credentials (seller's own store)
SP_API_REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN")
SP_API_CLIENT_ID     = os.getenv("SP_API_CLIENT_ID")
SP_API_CLIENT_SECRET = os.getenv("SP_API_CLIENT_SECRET")
SP_API_MARKETPLACE   = os.getenv("SP_API_MARKETPLACE", "A21TJRUUN4KGV")  # India

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://datathon_user:datathon_pass@localhost:5433/datathon_db"
)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Anthropic (used by Person 2 but declared here for shared config)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Scraper settings
REQUEST_DELAY_MIN     = float(os.getenv("REQUEST_DELAY_MIN", "2.0"))
REQUEST_DELAY_MAX     = float(os.getenv("REQUEST_DELAY_MAX", "5.0"))
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "3"))

# How many review pages to pull per product
MAX_REVIEW_PAGES = int(os.getenv("MAX_REVIEW_PAGES", "5"))

# Competitor detection thresholds
SIMILARITY_SAME_PRODUCT    = float(os.getenv("SIMILARITY_SAME_PRODUCT", "0.95"))
SIMILARITY_SIMILAR_PRODUCT = float(os.getenv("SIMILARITY_SIMILAR_PRODUCT", "0.80"))
SIMILARITY_TOP_K           = int(os.getenv("SIMILARITY_TOP_K", "10"))