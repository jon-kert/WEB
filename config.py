"""Configuration and constants for the oncology research app."""

import os
from dotenv import load_dotenv

load_dotenv()

# PubMed / PyMed Configuration
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
PUBMED_TOOL = os.getenv("PUBMED_TOOL", "OncologyResearchArticleDiscovery")
PUBMED_MAX_RESULTS = int(os.getenv("PUBMED_MAX_RESULTS", "100"))

# CSV Configuration
CSV_EXPORT_DIR = "exports"
PAPERS_TO_READ_FILE = "papers_to_read.csv"

# App Configuration
MIN_KEYWORD_MATCH = 2  # Minimum keywords in title to record article
APP_TITLE = "W.E.B. | Research Breadth Tool"
