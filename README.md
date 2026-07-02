# Research Breadth Tool

A Streamlit application for streamlining oncology research by querying PubMed for relevant articles, filtering by keyword criteria, and managing a review workflow.

## Features

- **PubMed Search**: Query PubMed with a comma-separated keyword list built into an OR query across all fields.
- **Smart Filtering**: Automatically filter articles based on keyword matches in titles & abstracts
- **Bookmarking**: Mark papers for thorough reading and maintain a review queues
- **Flexible Export**: Export bookmarked papers for manual review in csv or xlsx format, with control over which fields to include
- **Simple Interface**: Multi-tab UI for search, export, and paper management
- **Isolated Sessions**: Each users authentification, search results, and bookmarks are isolated from other users. There is no shared state.



# W.E.B. | Research Breadth Tool

A Streamlit application for streamlining oncology research by querying PubMed for relevant articles, filtering by keyword criteria, bookmarking articles of interest, and exporting results in multiple formats.

## Features

- **PubMed Search**: Query PubMed using a comma-separated keyword list, built into an OR query across all fields
- **Smart Filtering**: Filter returned articles by the number of unique keyword matches found across titles and abstracts
- **Bookmarking**: Save articles of interest to a personal review queue within your session
- **Flexible Export**: Export bookmarked articles to CSV or Excel, with control over which fields to include
- **Session Isolation**: Each user's search results and bookmarks are fully isolated — no shared state between users

## Requirements

- Python 3.12 or 3.13
- An NCBI email address (required by PubMed for API access)
- An NCBI API key (optional, but recommended for higher rate limits)

To generate an API key, visit [NCBI Account Settings](https://www.ncbi.nlm.nih.gov/account/settings/).

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/W.E.B.git
cd W.E.B.
```

**2. Create and activate a virtual environment:**
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. (Mac only) Install SSL certificates:**
```bash
open /Applications/Python\ 3.13/Install\ Certificates.command
```

**5. Run the app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

### Workflow

1. **Sidebar** — Enter your NCBI email address and optional API key. Adjust the minimum keyword match threshold (default: 2).

2. **Search Articles (Tab 1)** — Enter comma-separated keywords and click Search. W.E.B. queries PubMed and filters results by keyword matches across titles and abstracts. Click ➕ Bookmark on any article to save it for export.

3. **Bookmarked Papers (Tab 2)** — Review your saved articles. Remove any you no longer want with the ✕ button.

4. **Review & Export (Tab 3)** — Select which fields to include in your export, preview the table, then download as CSV or Excel.

5. **About (Tab 4)** — Overview of the tool and usage notes.

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── config.py           # Configuration and constants
├── library_client.py   # PubMed client using BioPython Entrez
├── csv_manager.py      # CSV and Excel export utilities
├── paper_manager.py    # Paper storage (legacy, preserved for reference)
├── requirements.txt    # Python dependencies
├── cmds.txt            # Handy terminal commands
└── README.md           # This file
```

## Configuration

`config.py` exposes the following constants:

| Constant | Default | Description |
|---|---|---|
| `MIN_KEYWORD_MATCH` | `2` | Default slider value for minimum keyword matches |
| `PUBMED_MAX_RESULTS` | `100` | Max articles fetched per search |
| `CSV_EXPORT_DIR` | `exports/` | Directory for exported files |
| `APP_TITLE` | `W.E.B. \| Research Breadth Tool` | App display title |

These can also be overridden via environment variables in a `.env` file.

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | DataFrame display |
| `biopython` | NCBI Entrez API client |
| `openpyxl` | Excel export |
| `reportlab` | PDF export (available, not yet wired to UI) |
| `python-dotenv` | `.env` file support |

## Notes

- **Session-based bookmarks**: Bookmarks live in Streamlit session state and are cleared on page refresh. Export before closing your tab.
- **No credentials are stored**: Email and API key are entered at runtime and never saved by the app.
- **Rate limiting**: Without an API key, NCBI allows 3 requests/second. With one, you get 10/second. W.E.B. respects these limits automatically.
