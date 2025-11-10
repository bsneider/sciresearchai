#!/usr/bin/env python3
"""
Local PubMed Data Loader for Bach Research System
Reads PubMed CSV files from https://github.com/sergeicu/aiscientist/tree/main/data

Provides fast local search across ~20k PubMed articles from Boston Children's Hospital.
CSV format: pmid, title, abstract, authors, journal, year, doi
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import pandas as pd
from dataclasses import dataclass


@dataclass
class LocalPubMedConfig:
    """Configuration for local PubMed data source"""
    data_path: Optional[str] = None  # Path to CSV file
    cache_dataframe: bool = True  # Cache DataFrame in memory
    min_match_score: float = 0.1  # Minimum relevance score threshold


class LocalPubMedDataLoader:
    """
    Loads and searches local PubMed CSV data.
    
    Compatible with CSV format from sergeicu/aiscientist repo:
    - Required columns: pmid, abstract
    - Optional columns: title, authors, journal, year, doi
    """
    
    def __init__(self, config: Optional[LocalPubMedConfig] = None):
        self.config = config or LocalPubMedConfig()
        self.df: Optional[pd.DataFrame] = None
        self.data_path: Optional[Path] = None
        self._initialized = False
        
        # Auto-detect data path if not provided
        if not self.config.data_path:
            self.config.data_path = self._find_data_file()
    
    def _find_data_file(self) -> Optional[str]:
        """Auto-detect PubMed data CSV in common locations"""
        # Search order: repo root data/, parent dirs, explicit env var
        search_paths = [
            "data/pubmed_data_2000.csv",
            "data/pubmed_data.csv",
            "../data/pubmed_data_2000.csv",
            "../data/pubmed_data.csv",
            "../../data/pubmed_data_2000.csv",
            "../../data/pubmed_data.csv",
        ]
        
        # Check environment variable first
        env_path = os.getenv("LOCAL_PUBMED_DATA_PATH")
        if env_path:
            search_paths.insert(0, env_path)
        
        # Try each path
        for path_str in search_paths:
            path = Path(path_str)
            if path.exists() and path.is_file():
                logging.info(f"Found local PubMed data: {path.absolute()}")
                return str(path.absolute())
        
        logging.warning("Local PubMed data file not found. Set LOCAL_PUBMED_DATA_PATH environment variable.")
        return None
    
    def initialize(self) -> bool:
        """Load CSV data into memory"""
        if self._initialized:
            return True
        
        if not self.config.data_path:
            logging.error("No data path configured for local PubMed loader")
            return False
        
        try:
            self.data_path = Path(self.config.data_path)
            if not self.data_path.exists():
                logging.error(f"Data file not found: {self.data_path}")
                return False
            
            logging.info(f"Loading local PubMed data from: {self.data_path}")
            
            # Load CSV with flexible encoding
            try:
                self.df = pd.read_csv(self.data_path, encoding='utf-8')
            except UnicodeDecodeError:
                logging.warning("UTF-8 decoding failed, trying latin-1")
                self.df = pd.read_csv(self.data_path, encoding='latin-1')
            
            # Normalize column names to lowercase for easy access
            self.df.columns = [c.lower() for c in self.df.columns]

            # Map abstract_text to abstract if needed
            if 'abstract_text' in self.df.columns and 'abstract' not in self.df.columns:
                self.df.rename(columns={'abstract_text': 'abstract'}, inplace=True)

            # Validate required columns
            required_cols = ['pmid', 'abstract']
            missing_cols = [col for col in required_cols if col not in self.df.columns]

            if missing_cols:
                logging.error(f"Missing required columns: {missing_cols}")
                logging.error(f"Available columns: {list(self.df.columns)}")
                return False
            
            # Drop rows with empty abstracts
            initial_count = len(self.df)
            abstract_col = 'abstract' if 'abstract' in self.df.columns else 'abstract_text'
            self.df = self.df[self.df[abstract_col].notna() & (self.df[abstract_col].str.strip() != '')]
            final_count = len(self.df)
            
            if final_count < initial_count:
                logging.info(f"Filtered out {initial_count - final_count} rows with empty abstracts")
            
            logging.info(f"Loaded {final_count} articles from local PubMed data")
            self._initialized = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to load local PubMed data: {e}")
            return False
    
    def search(self, query: str, limit: int = 100, 
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search local PubMed data by keyword matching in title and abstract.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters (year_range, min_score, etc.)
        
        Returns:
            List of standardized paper dictionaries
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        if self.df is None or len(self.df) == 0:
            return []
        
        try:
            # Prepare search terms (simple keyword matching for now)
            query_lower = query.lower()
            query_terms = query_lower.split()
            
            # Score each article based on keyword matches
            def score_article(row) -> float:
                """Simple relevance scoring based on term frequency"""
                score = 0.0

                # Search in abstract (weight: 1.0)
                abstract_text = str(row.get('abstract', '') or row.get('abstract_text', '')).lower()
                for term in query_terms:
                    if term in abstract_text:
                        score += abstract_text.count(term) * 1.0
                
                # Search in title (weight: 2.0 - title matches are more important)
                if 'title' in row and pd.notna(row['title']):
                    title_text = str(row['title']).lower()
                    for term in query_terms:
                        if term in title_text:
                            score += title_text.count(term) * 2.0
                
                # Normalize by number of terms
                return score / len(query_terms) if query_terms else 0.0
            
            # Score all articles
            self.df['_relevance_score'] = self.df.apply(score_article, axis=1)
            
            # Filter by minimum score
            min_score = self.config.min_match_score
            if filters and 'min_score' in filters:
                min_score = filters['min_score']
            
            results_df = self.df[self.df['_relevance_score'] > min_score].copy()
            
            # Apply year range filter if provided
            if filters and 'year_range' in filters:
                year_min, year_max = filters['year_range']
                year_col = 'year' if 'year' in results_df.columns else 'publication_year'
                if year_col in results_df.columns:
                    results_df = results_df[
                        (results_df[year_col] >= year_min) & (results_df[year_col] <= year_max)
                    ]
            
            # Sort by relevance score (descending)
            results_df = results_df.sort_values('_relevance_score', ascending=False)
            
            # Limit results
            results_df = results_df.head(limit)
            
            # Convert to standardized format
            papers = []
            for _, row in results_df.iterrows():
                paper = self._row_to_standard_format(row)
                papers.append(paper)
            
            # Clean up temporary score column
            if '_relevance_score' in self.df.columns:
                self.df.drop('_relevance_score', axis=1, inplace=True)
            
            logging.info(f"Local PubMed search found {len(papers)} results for '{query}'")
            return papers
            
        except Exception as e:
            logging.error(f"Local PubMed search failed: {e}")
            return []
    
    def _row_to_standard_format(self, row: pd.Series) -> Dict[str, Any]:
        """Convert DataFrame row to standardized paper format"""
        paper = {
            'id': str(row.get('pmid', '')),
            'pmid': str(row.get('pmid', '')),
            'title': str(row.get('title', '')) if pd.notna(row.get('title')) else '',
            'abstract': str(row.get('abstract', '') or row.get('abstract_text', '')),
            'source': 'local_pubmed',
            'retrieved_at': datetime.now().isoformat()
        }
        
        # Add optional fields
        if 'authors' in row and pd.notna(row['authors']):
            # Parse authors string into list of dicts
            authors_str = str(row['authors'])
            paper['authors'] = [{'name': name.strip()} for name in authors_str.split(',')]
        else:
            paper['authors'] = []
        
        year_val = row.get('year') or row.get('publication_year')
        if year_val and pd.notna(year_val):
            try:
                paper['year'] = int(year_val)
            except (ValueError, TypeError):
                paper['year'] = None
        else:
            paper['year'] = None

        journal_val = row.get('journal') or row.get('journal_title')
        if journal_val and pd.notna(journal_val):
            paper['journal'] = str(journal_val)
            paper['venue'] = str(journal_val)
        
        if 'doi' in row and pd.notna(row['doi']):
            paper['doi'] = str(row['doi'])
            paper['url'] = f"https://doi.org/{row['doi']}"
        
        # Add relevance score if present
        if '_relevance_score' in row:
            paper['quality_score'] = float(row['_relevance_score'])
        
        return paper
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded dataset"""
        if not self._initialized or self.df is None:
            return {
                'initialized': False,
                'total_articles': 0
            }
        
        stats = {
            'initialized': True,
            'total_articles': len(self.df),
            'data_source': str(self.data_path) if self.data_path else None,
            'columns': list(self.df.columns)
        }
        
        # Year distribution
        year_col = 'year' if 'year' in self.df.columns else 'publication_year'
        if year_col in self.df.columns:
            year_counts = self.df[year_col].value_counts().to_dict()
            stats['year_distribution'] = dict(sorted(year_counts.items()))
            stats['year_range'] = (
                int(self.df[year_col].min()) if pd.notna(self.df[year_col].min()) else None,
                int(self.df[year_col].max()) if pd.notna(self.df[year_col].max()) else None
            )
        
        return stats
    
    def is_available(self) -> bool:
        """Check if local data source is available"""
        return self._initialized and self.df is not None and len(self.df) > 0


# Convenience function for use in Bach search stack
async def search_local_pubmed(query: str, limit: int = 100, 
                            filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Async wrapper for local PubMed search (for compatibility with async search APIs).
    
    Args:
        query: Search query
        limit: Max results
        filters: Optional filters
    
    Returns:
        List of paper dictionaries
    """
    loader = LocalPubMedDataLoader()
    if not loader.initialize():
        return []
    
    return loader.search(query, limit, filters)


if __name__ == "__main__":
    # Example usage and testing
    import asyncio
    
    async def test_local_search():
        """Test local PubMed search"""
        print("Testing Local PubMed Data Loader")
        print("=" * 60)
        
        loader = LocalPubMedDataLoader()
        
        if not loader.initialize():
            print("ERROR: Failed to initialize loader")
            print("Set LOCAL_PUBMED_DATA_PATH environment variable or place data file in data/ directory")
            return
        
        # Get statistics
        stats = loader.get_statistics()
        print(f"\nDataset Statistics:")
        print(f"  Total Articles: {stats['total_articles']}")
        if 'year_range' in stats:
            print(f"  Year Range: {stats['year_range'][0]} - {stats['year_range'][1]}")
        print(f"  Columns: {', '.join(stats['columns'])}")
        
        # Test search
        print(f"\nSearching for 'Atrial fibrillation'...")
        results = loader.search("Atrial fibrillation", limit=10)
        
        print(f"\nFound {len(results)} results:\n")
        for i, paper in enumerate(results[:5], 1):
            print(f"{i}. {paper.get('title', 'No title')}")
            print(f"   PMID: {paper.get('pmid')}")
            print(f"   Year: {paper.get('year', 'N/A')}")
            print(f"   Score: {paper.get('quality_score', 0):.2f}")
            print()
    
    asyncio.run(test_local_search())
