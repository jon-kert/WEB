"""Streamlit app for oncology research article discovery."""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import time

from config import APP_TITLE, MIN_KEYWORD_MATCH
from library_client import PubMedClient
from csv_manager import CSVManager, FIELD_LABELS, ALL_FIELDS


def initialize_session_state():
    """Initialize Streamlit session state variables."""

    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "filtered_results" not in st.session_state:
        st.session_state.filtered_results = []
    if "bookmarked_papers" not in st.session_state:
        st.session_state.bookmarked_papers = []


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="",
        layout="wide"
    )
    
    st.title(f"{APP_TITLE}")
    
    initialize_session_state()
    
    # Sidebar for inputting credentials and whatnot
    st.sidebar.header("PubMed Configuration")
    email = st.sidebar.text_input(
        "Email address",
        help="Required by PubMed/PyMed for identification"
    )
    api_key = st.sidebar.text_input(
        "NCBI API Key (optional)",
        type="password",
        help="Optional NCBI API key for higher request limits"
    )
    
    # slider for minimmum keyword matches
    min_keyword_match = st.sidebar.slider(
        "Minimum Keyword Matches",
        min_value = 1,
        max_value = 7,
        value = MIN_KEYWORD_MATCH,
        help = "Minimum keywords to find in article title"
    )
    
    # Main tabs - in order of workflow
    tab1, tab2, tab3, tab4 = st.tabs(["Search Articles", "Bookmarked Papers", "Review & Export", "About W.E.B."])
    
    with tab1:
        st.header("Search Articles")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            keywords_input = st.text_input(
                "Enter keywords (comma-separated)",
                placeholder="e.g., melanoma, immunotherapy, BRAF mutation"
            )
        with col2:
            search_button = st.button("Search", use_container_width=True)
        
        
        if search_button:
            if not email:
                st.error("Please enter your email address in the sidebar")
            elif not keywords_input:
                st.error("Please enter at least one keyword")
            else:
                keywords = [kw.strip() for kw in keywords_input.split(",")]
                
                with st.spinner("Searching PubMed..."):
                    try:
                        client = PubMedClient(email=email, api_key=api_key)
                        results = client.search(keywords)
                        
                        # Filter by keyword matches
                        filtered = client.filter_by_keywords(
                            results,
                            keywords,
                            min_matches = min_keyword_match
                        )
                        
                        st.session_state.search_results = results
                        st.session_state.filtered_results = filtered
                        
                        st.success(f"Found {len(results)} articles, {len(filtered)} meet keyword criteria")
                        
                    except Exception as e:
                        st.error(f"Search failed: {str(e)}")
        
        # Display search results
        if st.session_state.filtered_results:
            st.subheader(f"Filtered Results ({len(st.session_state.filtered_results)})")
            
            for i, article in enumerate(st.session_state.filtered_results):
                with st.expander(
                    f"[{article.get('keyword_matches', 0)} matches] {article.get('title', 'Untitled')[:80]}..."
                ):
                    st.write(f"**Title:** {article.get('title', 'N/A')}")
                    st.write(f"**Date Published:** {article.get('publication_date', 'N/A')}")
                    st.write(f"**Abstract:** {article.get('abstract', 'N/A')}")
                    st.write(f"**URL:** {article.get('url', 'N/A')}")
                    st.write(f"**Matched Keywords:** {', '.join(article.get('matching_keywords', 'N/A'))}")
                    

                    if st.button("➕ Bookmark", key=f"add_{i}"):
                        titles = [p.get("title") for p in st.session_state.bookmarked_papers]
                        if article.get("title") not in titles:
                            article["date_added"] = pd.Timestamp.now().isoformat()
                            st.session_state.bookmarked_papers.append(article)
                        st.success("Marked for review!")


    with tab2:
        st.header("Bookmarked Papers")
        
       
        papers = st.session_state.bookmarked_papers
        
        if not papers:
            st.info("No papers marked for review yet.")
        else:
            st.subheader(f"Papers in Queue ({len(papers)})")
            
            for i, paper in enumerate(papers):
                col1, col2 = st.columns([0.95, 0.05])
                
                with col1:
                    with st.expander(f"{paper.get('title', 'Untitled')[:70]}..."):
                        st.write(f"**Title:** {paper.get('title', 'N/A')}")
                        st.write(f"**Authors:** {paper.get('authors', 'N/A')}")
                        st.write(f"**Abstract:** {paper.get('abstract', 'N/A')}")
                        st.write(f"*Added: {paper.get('date_added', 'N/A')}*")
                
                with col2:
                    # and the remove button:
                    if st.button("✕", key=f"remove_{i}"):
                        st.session_state.bookmarked_papers = [
                            p for p in st.session_state.bookmarked_papers
                            if p.get("title") != paper.get("title")
                        ]
                        st.rerun()
    with tab3:
        st.header("Review & Export")
 
        papers = st.session_state.bookmarked_papers
 
        if not papers:
            st.info("No papers bookmarked yet. Search and bookmark articles first.")
        else:
            # ---- Field selection ----
            st.subheader("Select Fields to Export")
            
            all_labels = {f: FIELD_LABELS[f] for f in ALL_FIELDS}
            # Default everything on
            if "export_fields" not in st.session_state:
                st.session_state.export_fields = ALL_FIELDS.copy()
 
            cols = st.columns(4)
            selected_fields = []
            for idx, (field, label) in enumerate(all_labels.items()):
                checked = cols[idx % 4].checkbox(
                    label,
                    value=field in st.session_state.export_fields,
                    key=f"field_{field}"
                )
                if checked:
                    selected_fields.append(field)
 
            if not selected_fields:
                st.warning("Select at least one field to preview and export.")
            else:
 
                # Preview table to check before export
                st.subheader(f"Bookmarked Articles ({len(papers)})")
                df_data = []
                for article in papers:
                    row = {}
                    for f in selected_fields:
                        val = article.get(f, "N/A")
                        if isinstance(val, list):
                            val = ", ".join(val)
                        label = FIELD_LABELS.get(f, f)
                        # Truncate title for display only
                        if f == "title" and isinstance(val, str):
                            val = val[:70]
                        row[label] = val
                    df_data.append(row)
 
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
 
                st.divider()
 
                # Export Buttons | CSV and Excel ... could add pdf / other file types later...
                st.subheader("Export Options")
                exp_col1, exp_col2, exp_col3 = st.columns(3)
 
                csv_mgr = CSVManager()
                ts = int(time.time())
 
                # CSV Export
                with exp_col1:
                    if st.button("Export to CSV", use_container_width=True):
                        try:
                            filepath = csv_mgr.export_csv(
                                papers,
                                filename=f"{ts}-articles.csv",
                                fields=selected_fields,
                            )
                            with open(filepath, "r", encoding="utf-8") as f:
                                st.download_button(
                                    label="⬇ Download CSV",
                                    data=f.read(),
                                    file_name=f"{ts}-articles.csv",
                                    mime="text/csv",
                                    key="dl_csv"
                                )
                        except Exception as e:
                            st.error(f"CSV export failed: {str(e)}")

                # Excel Export
                with exp_col2:
                    if st.button("Export to Excel", use_container_width=True):
                        try:
                            filepath = csv_mgr.export_excel(
                                papers,
                                filename=f"{ts}-articles.xlsx",
                                fields=selected_fields,
                            )
                            with open(filepath, "rb") as f:
                                st.download_button(
                                    label="⬇ Download Excel",
                                    data=f.read(),
                                    file_name=f"{ts}-articles.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="dl_xlsx"
                                )
                        except Exception as e:
                            st.error(f"Excel export failed: {str(e)}")
                
                # potentially add PDF export in the future ..? Any other formats?
                #with exp_col2:
                #    if st.button("Export to PDF", use_container_width=True):
    
  
    with tab4:
        st.header("About W.E.B.")
        st.markdown("""
        **W.E.B.** (Workflow for Erudition and Brilliance) is a framework designed to help researchers discover and manage research articles from PubMed. 
        Using a comma-separated list of keywords, W.E.B. queries PubMed then filters results based on the number of keyword matches in the article titles and abstracts.

        **How to Use:**
        1. Enter your NHIC email address and PubMed API key in the sidebar.
        2. Enter your comma-separated keywords in the search tab.
        3. Click "Search" to fetch matching articles from PubMed.
        4. Read through the abstracts of filtered results, and add articles of interest into the "Papers to Read" list.
        5. Export your list of freshly picked articles to CSV for further review or sharing.

        
        **Note:** The generate your own API Key, please visit [NCBI API Key](https://www.ncbi.nlm.nih.gov/account/settings/) 
                    
        **Store your API key somewhere SECURE | This tool does NOT save anyone's credentials.**
        """)


if __name__ == "__main__":
    main()
