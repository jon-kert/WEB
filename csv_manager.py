"""Manager for article export in CSV, Excel, and PDF formats."""

import os
import csv
import io
from typing import List, Dict, Any, Optional

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from config import CSV_EXPORT_DIR


# All article fields and their display labels, in preferred column order
FIELD_LABELS = {
    "title":                "Title",
    "publication_date":     "Date Published",
    "pubmed_id":            "PubMed ID",
    "url":                  "URL",
    "authors":              "Authors",
    "abstract":             "Abstract",
    "matching_keywords":    "Matched Keywords",
    "keyword_matches":      "Num Keyword Matches",
}

ALL_FIELDS = list(FIELD_LABELS.keys())


class ExportManager:
    """Handle article export to CSV, Excel, and PDF."""

    def __init__(self, export_dir: str = CSV_EXPORT_DIR):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def _filepath(self, filename: str) -> str:
        return os.path.join(self.export_dir, filename)

    def _prepare_rows(
        self,
        articles: List[Dict[str, Any]],
        fields: Optional[List[str]] = None,
    ) -> tuple[list, list]:
        """
        Return (headers, rows) for the selected fields.
        matching_keywords lists are joined into a comma-separated string.
        """
        if not fields:
            fields = ALL_FIELDS

        headers = [FIELD_LABELS.get(f, f) for f in fields]
        rows = []
        for article in articles:
            row = []
            for f in fields:
                val = article.get(f, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                row.append(str(val) if val is not None else "")
            rows.append(row)

        return headers, rows

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------
    def export_csv(
        self,
        articles: List[Dict[str, Any]],
        filename: str,
        fields: Optional[List[str]] = None,
    ) -> str:
        if not articles:
            raise ValueError("No articles to export.")

        headers, rows = self._prepare_rows(articles, fields)
        filepath = self._filepath(filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        return filepath

    # ------------------------------------------------------------------
    # Excel
    # ------------------------------------------------------------------
    def export_excel(
        self,
        articles: List[Dict[str, Any]],
        filename: str,
        fields: Optional[List[str]] = None,
    ) -> str:
        if not articles:
            raise ValueError("No articles to export.")

        headers, rows = self._prepare_rows(articles, fields)
        filepath = self._filepath(filename)

        wb = Workbook()
        ws = wb.active
        ws.title = "Articles"

        # Header row styling
        header_fill = PatternFill("solid", start_color="1F4E79")
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        # Data rows
        row_font = Font(name="Arial", size=10)
        wrap_align = Alignment(vertical="top", wrap_text=True)
        alt_fill = PatternFill("solid", start_color="EBF3FB")

        for row_idx, row in enumerate(rows, start=2):
            fill = alt_fill if row_idx % 2 == 0 else None
            for col_idx, value in enumerate(row, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.font = row_font
                cell.alignment = wrap_align
                if fill:
                    cell.fill = fill

        # Column widths
        col_widths = {
            "Title": 45,
            "Abstract": 60,
            "URL": 40,
            "Authors": 30,
            "Matched Keywords": 30,
        }
        for col_idx, header in enumerate(headers, start=1):
            width = col_widths.get(header, 18)
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = width

        ws.row_dimensions[1].height = 30
        ws.freeze_panes = "A2"

        wb.save(filepath)
        return filepath



# ---------------------------------------------------------------------------
# Backwards-compatible alias so existing app.py imports still work
# ---------------------------------------------------------------------------
class CSVManager(ExportManager):
    """Alias kept for backwards compatibility."""

    def export_articles(
        self,
        articles: List[Dict[str, Any]],
        filename: str = None,
        fields: Optional[List[str]] = None,
    ) -> str:
        if not filename:
            from datetime import datetime
            filename = f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "xlsx":
            return self.export_excel(articles, filename, fields)
        elif ext == "pdf":
            return self.export_pdf(articles, filename, fields)
        else:
            return self.export_csv(articles, filename, fields)