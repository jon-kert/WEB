"""Manager for papers marked for thorough review."""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
from config import PAPERS_TO_READ_FILE


class PaperManager:
    """Manage papers marked for thorough review."""
    
    def __init__(self, storage_file: str = PAPERS_TO_READ_FILE):
        """Initialize paper manager."""
        self.storage_file = storage_file
        self._ensure_file()
    
    def _ensure_file(self) -> None:
        """Create storage file if it doesn't exist."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w") as f:
                json.dump([], f)
    
    def add_paper(self, article: Dict[str, Any]) -> None:
        """
        Add paper to review list.
        
        Args:
            article: Article dictionary with title, abstract, etc.
        """
        papers = self.get_all_papers()
        
        # Avoid duplicates by checking title
        if not any(p.get("title") == article.get("title") for p in papers):
            article["date_added"] = datetime.now().isoformat()
            papers.append(article)
            self._save_papers(papers)
    
    def remove_paper(self, title: str) -> None:
        """
        Remove paper from review list by title.
        
        Args:
            title: Title of paper to remove
        """
        papers = self.get_all_papers()
        papers = [p for p in papers if p.get("title") != title]
        self._save_papers(papers)
    
    def get_all_papers(self) -> List[Dict[str, Any]]:
        """Get all papers in review list."""
        with open(self.storage_file, "r") as f:
            return json.load(f)
    
    def _save_papers(self, papers: List[Dict[str, Any]]) -> None:
        """Save papers to storage file."""
        with open(self.storage_file, "w") as f:
            json.dump(papers, f, indent=2)
