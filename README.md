# Oncology Research Article Discovery

A Streamlit application for streamlining oncology research by querying PubMed for relevant articles, filtering by keyword criteria, and managing a review workflow.

## Features

- **Library Search**: Query PubMed with keywords and optional NCBI API authentication
- **Smart Filtering**: Automatically filter articles based on keyword matches in titles
- **CSV Export**: Export filtered results for manual review
- **Paper Triage**: Mark papers for thorough reading and maintain a review queue
- **Simple Interface**: Multi-tab UI for search, export, and paper management

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your PubMed identification details:
   ```bash
   cp .env.example .env
   # Edit .env and add your PUBMED_EMAIL and optional PUBMED_API_KEY
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Workflow

1. **Search Articles** (Tab 1):
   - Enter keywords separated by commas
   - Set minimum keyword matches threshold
   - View filtered articles that meet your criteria
   - Add papers to your review queue

2. **Review & Export** (Tab 2):
   - View all filtered articles in a table
   - Export results to CSV for offline review

3. **Papers to Read** (Tab 3):
   - View all papers marked for thorough reading
   - Remove papers as you complete them

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── config.py           # Configuration and constants
├── library_client.py   # UM library API client
├── csv_manager.py      # CSV import/export utilities
├── paper_manager.py    # Paper tracking and storage
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Configuration

Edit `config.py` to customize:
- Minimum keyword matches threshold
- CSV export directory
- API endpoint URL

## Storage

- **papers_to_read.json**: JSON file storing papers marked for review
- **exports/**: Directory containing exported CSV files

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Requests

## Notes

- PubMed requires a valid email address for API access
- NCBI API key is optional but recommended for heavier use
- CSV exports are timestamped to avoid overwrites
