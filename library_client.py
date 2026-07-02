"""Client for querying PubMed via BioPython Entrez — no pymed/PIL dependency."""

import re
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

from Bio import Entrez

from config import PUBMED_EMAIL, PUBMED_API_KEY, PUBMED_TOOL, PUBMED_MAX_RESULTS


class PubMedClient:
    """Interface for querying PubMed through BioPython Entrez."""

    def __init__(
        self,
        email: str = PUBMED_EMAIL,
        api_key: str = PUBMED_API_KEY,
        tool: str = PUBMED_TOOL,
    ):
        self.email = email
        self.api_key = api_key
        self.tool = tool

    def _configure_entrez(self):
        """Set BioPython Entrez credentials."""
        Entrez.email = self.email
        Entrez.tool = self.tool
        if self.api_key:
            Entrez.api_key = self.api_key

    def _build_query(self, keywords: List[str]) -> str:
        """
        Build a PubMed OR query from keywords.
        e.g. ["melanoma", "BRAF mutation"] ->
             '("melanoma"[All Fields]) OR ("BRAF mutation"[All Fields])'
        """
        terms = [f'("{kw.strip()}"[All Fields])' for kw in keywords if kw.strip()]
        return " OR ".join(terms)

    def _parse_article(self, article_xml, keywords: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a single PubMed article XML element into a result dict."""
        try:
            # PubMed ID
            pubmed_id = ""
            pmid_el = article_xml.find(".//PMID")
            if pmid_el is not None and pmid_el.text:
                pubmed_id = pmid_el.text.strip()

            # Title
            title_el = article_xml.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""

            # Abstract — may have multiple AbstractText elements
            abstract_parts = []
            for ab in article_xml.findall(".//AbstractText"):
                text = "".join(ab.itertext()).strip()
                if text:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)

            # Authors
            authors = []
            for author in article_xml.findall(".//Author"):
                last = author.findtext("LastName") or ""
                first = author.findtext("ForeName") or ""
                name = " ".join(p for p in [first, last] if p).strip()
                if name:
                    authors.append(name)

            # Publication date — prefer MedlineDate, fall back to Year/Month
            pub_date = ""
            date_el = article_xml.find(".//PubDate")
            if date_el is not None:
                medline = date_el.findtext("MedlineDate")
                if medline:
                    pub_date = medline.strip()
                else:
                    year  = date_el.findtext("Year") or ""
                    month = date_el.findtext("Month") or ""
                    pub_date = " ".join(p for p in [year, month] if p).strip()

            # Matched keywords
            combined_text = title + " " + abstract
            found_keywords = list({
                kw for kw in keywords
                if kw.lower() in combined_text.lower()
            })

            return {
                "title": title,
                "abstract": abstract,
                "authors": ", ".join(authors) if authors else "N/A",
                "pubmed_id": pubmed_id,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/" if pubmed_id else "",
                "publication_date": pub_date or "N/A",
                "matching_keywords": found_keywords,
            }

        except Exception:
            return None

    def search(self, keywords: List[str], query: str = None) -> List[Dict[str, Any]]:
        """
        Search PubMed for articles using ESearch + EFetch.

        Args:
            keywords: List of keywords to search for
            query: Optional custom query string (overrides keyword building)

        Returns:
            List of article result dicts
        """
        if not self.email:
            raise ValueError("Email address is required for PubMed queries.")

        self._configure_entrez()
        search_query = query or self._build_query(keywords)

        try:
            # Step 1 — ESearch: get list of PMIDs
            search_handle = Entrez.esearch(
                db="pubmed",
                term=search_query,
                retmax=PUBMED_MAX_RESULTS,
                usehistory="y",
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            pmids = search_results.get("IdList", [])
            if not pmids:
                return []

            # Step 2 — EFetch: retrieve full records in batches of 100
            results: List[Dict[str, Any]] = []
            batch_size = 100

            for start in range(0, len(pmids), batch_size):
                batch = pmids[start: start + batch_size]
                fetch_handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch),
                    rettype="xml",
                    retmode="xml",
                )
                raw_xml = fetch_handle.read()
                fetch_handle.close()

                root = ET.fromstring(raw_xml)
                for article_xml in root.findall(".//PubmedArticle"):
                    parsed = self._parse_article(article_xml, keywords)
                    if parsed:
                        results.append(parsed)

                # Respect NCBI rate limit between batches
                if start + batch_size < len(pmids):
                    time.sleep(0.34)

            return results

        except Exception as e:
            raise Exception(f"PubMed query failed: {str(e)}")

    def _tokenize(self, text: str) -> str:
        """Lowercase and collapse whitespace for reliable substring matching."""
        return re.sub(r"\s+", " ", text.lower().strip())

    def filter_by_keywords(
        self,
        articles: List[Dict[str, Any]],
        keywords: List[str],
        min_matches: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Filter articles by unique keyword matches across title and abstract.

        Args:
            articles: List of article result dicts
            keywords: List of keywords to check
            min_matches: Minimum unique keywords that must appear

        Returns:
            Filtered list sorted by match count descending
        """
        filtered = []
        norm_keywords = [self._tokenize(kw) for kw in keywords if kw.strip()]

        for article in articles:
            title    = self._tokenize(article.get("title", ""))
            abstract = self._tokenize(article.get("abstract", ""))

            matched = [kw for kw in norm_keywords if kw in title or kw in abstract]
            t_matches = sum(1 for kw in norm_keywords if kw in title)
            a_matches = sum(1 for kw in norm_keywords if kw in abstract)

            if len(matched) >= min_matches:
                article["keyword_matches"] = len(matched)
                article["title_keyword_matches"] = t_matches
                article["abstract_keyword_matches"] = a_matches
                filtered.append(article)

        filtered.sort(key=lambda a: a["keyword_matches"], reverse=True)
        return filtered