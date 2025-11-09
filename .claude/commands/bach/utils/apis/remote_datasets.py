#!/usr/bin/env python3
"""
Remote Dataset Search Integration for Bach Research System
Comprehensive access to remote scientific datasets, databases, and repositories

Provides unified interface to:
- Scientific data repositories (Zenodo, Figshare, Dataverse)
- Government research databases (NIH, NSF, EU repositories)
- Domain-specific databases (GenBank, PDB, ChEMBL)
- Real-time monitoring systems
- Cloud-based research platforms
"""

import asyncio
import aiohttp
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET


class DatasetType(Enum):
    """Types of datasets available"""
    GENOMIC = "genomic"
    CLINICAL = "clinical"
    IMAGING = "imaging"
    TEXT = "text"
    NUMERICAL = "numerical"
    MIXED = "mixed"
    EXPERIMENTAL = "experimental"


@dataclass
class DatasetInfo:
    """Standardized dataset information"""
    id: str
    title: str
    description: str
    authors: List[str]
    repository: str
    dataset_type: DatasetType
    size_mb: Optional[float]
    format: List[str]
    license: Optional[str]
    access_url: str
    doi: Optional[str]
    keywords: List[str]
    last_updated: Optional[datetime]
    download_count: Optional[int]
    citation_count: Optional[int]
    metadata: Dict[str, Any]


class NCBIDatasetAPI:
    """NCBI datasets and genomic data access"""
    
    def __init__(self):
        self.base_url = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha"
        self.sra_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def search_genomes(self, query: str, limit: int = 100) -> List[DatasetInfo]:
        """Search NCBI genome datasets"""
        try:
            session = await self._get_session()
            
            params = {
                "search_text": query,
                "limit": min(limit, 1000)
            }
            
            async with session.get(f"{self.base_url}/genome/dataset_report", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_genome_data(data)
                else:
                    logging.error(f"NCBI genome search error: {response.status}")
                    return []
                    
        except Exception as e:
            logging.error(f"NCBI genome search error: {e}")
            return []
    
    async def search_sra(self, query: str, limit: int = 100) -> List[DatasetInfo]:
        """Search NCBI Sequence Read Archive"""
        try:
            session = await self._get_session()
            
            # First search for IDs
            search_params = {
                "db": "sra",
                "term": query,
                "retmax": min(limit, 1000),
                "retmode": "json"
            }
            
            async with session.get(f"{self.sra_base}/esearch.fcgi", params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    id_list = search_data.get("esearchresult", {}).get("idlist", [])
                    
                    if not id_list:
                        return []
                    
                    # Fetch detailed records
                    fetch_params = {
                        "db": "sra",
                        "id": ",".join(id_list),
                        "rettype": "runinfo",
                        "retmode": "text"
                    }
                    
                    async with session.get(f"{self.sra_base}/efetch.fcgi", params=fetch_params) as fetch_response:
                        if fetch_response.status == 200:
                            csv_data = await fetch_response.text()
                            return self._parse_sra_csv(csv_data)
                        else:
                            return []
                else:
                    return []
                    
        except Exception as e:
            logging.error(f"NCBI SRA search error: {e}")
            return []
    
    def _parse_genome_data(self, data: Dict[str, Any]) -> List[DatasetInfo]:
        """Parse NCBI genome data response"""
        datasets = []
        
        for report in data.get("reports", []):
            try:
                assembly = report.get("assembly_info", {})
                organism = report.get("organism", {})
                
                dataset = DatasetInfo(
                    id=assembly.get("assembly_accession", ""),
                    title=f"{organism.get('organism_name', 'Unknown')} genome assembly",
                    description=f"Genome assembly for {organism.get('organism_name', 'Unknown organism')}",
                    authors=[assembly.get("submitter", "Unknown")],
                    repository="ncbi_genomes",
                    dataset_type=DatasetType.GENOMIC,
                    size_mb=assembly.get("total_sequence_length", 0) / 1000000,  # Convert to MB
                    format=["FASTA", "GFF"],
                    license="Public Domain",
                    access_url=f"https://www.ncbi.nlm.nih.gov/assembly/{assembly.get('assembly_accession', '')}",
                    doi=None,
                    keywords=[organism.get("tax_id", ""), "genome", "assembly"],
                    last_updated=datetime.fromisoformat(assembly.get("submission_date", "1970-01-01").replace("Z", "+00:00")) if assembly.get("submission_date") else None,
                    download_count=None,
                    citation_count=None,
                    metadata={
                        "assembly_level": assembly.get("assembly_level"),
                        "genome_representation": assembly.get("genome_representation"),
                        "contig_count": assembly.get("contig_count"),
                        "scaffold_count": assembly.get("scaffold_count")
                    }
                )
                
                datasets.append(dataset)
                
            except Exception as e:
                logging.warning(f"Error parsing genome entry: {e}")
                continue
        
        return datasets
    
    def _parse_sra_csv(self, csv_data: str) -> List[DatasetInfo]:
        """Parse SRA CSV data"""
        datasets = []
        lines = csv_data.strip().split('\n')
        
        if len(lines) < 2:
            return datasets
        
        headers = lines[0].split(',')
        
        for line in lines[1:]:
            try:
                fields = line.split(',')
                if len(fields) != len(headers):
                    continue
                
                record = dict(zip(headers, fields))
                
                dataset = DatasetInfo(
                    id=record.get("Run", ""),
                    title=f"SRA Run {record.get('Run', 'Unknown')}",
                    description=f"Sequencing run from {record.get('Experiment', 'Unknown experiment')}",
                    authors=[record.get("submitter_id", "Unknown")],
                    repository="ncbi_sra",
                    dataset_type=DatasetType.GENOMIC,
                    size_mb=float(record.get("size_MB", 0)) if record.get("size_MB") else None,
                    format=["FASTQ", "SRA"],
                    license="Public Domain",
                    access_url=f"https://www.ncbi.nlm.nih.gov/sra/{record.get('Run', '')}",
                    doi=None,
                    keywords=[record.get("LibraryStrategy", ""), record.get("Platform", ""), "sequencing"],
                    last_updated=datetime.fromisoformat(record.get("ReleaseDate", "1970-01-01")) if record.get("ReleaseDate") else None,
                    download_count=None,
                    citation_count=None,
                    metadata={
                        "platform": record.get("Platform"),
                        "library_strategy": record.get("LibraryStrategy"),
                        "library_source": record.get("LibrarySource"),
                        "library_selection": record.get("LibrarySelection"),
                        "bases": record.get("bases"),
                        "spots": record.get("spots")
                    }
                )
                
                datasets.append(dataset)
                
            except Exception as e:
                logging.warning(f"Error parsing SRA entry: {e}")
                continue
        
        return datasets
    
    async def close(self):
        if self.session:
            await self.session.close()


class EBIDatasetAPI:
    """European Bioinformatics Institute dataset access"""
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/ebisearch/ws/rest"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def search_datasets(self, query: str, databases: Optional[List[str]] = None, 
                            limit: int = 100) -> List[DatasetInfo]:
        """Search EBI datasets across multiple databases"""
        if databases is None:
            databases = ["pride", "arrayexpress", "ena", "chembl"]
        
        all_datasets = []
        
        for db in databases:
            try:
                db_datasets = await self._search_single_database(db, query, limit)
                all_datasets.extend(db_datasets)
            except Exception as e:
                logging.error(f"Error searching EBI database {db}: {e}")
                continue
        
        return all_datasets
    
    async def _search_single_database(self, database: str, query: str, limit: int) -> List[DatasetInfo]:
        """Search single EBI database"""
        session = await self._get_session()
        
        params = {
            "query": query,
            "format": "json",
            "size": min(limit, 1000)
        }
        
        async with session.get(f"{self.base_url}/{database}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_ebi_data(data, database)
            else:
                logging.warning(f"EBI {database} search failed: {response.status}")
                return []
    
    def _parse_ebi_data(self, data: Dict[str, Any], database: str) -> List[DatasetInfo]:
        """Parse EBI search results"""
        datasets = []
        
        entries = data.get("entries", [])
        
        for entry in entries:
            try:
                # Extract fields (structure varies by database)
                fields = entry.get("fields", {})
                
                dataset_type = self._determine_dataset_type(database, fields)
                
                dataset = DatasetInfo(
                    id=entry.get("id", ""),
                    title=fields.get("title", ["Unknown"])[0] if fields.get("title") else "Unknown",
                    description=fields.get("description", [""])[0] if fields.get("description") else "",
                    authors=fields.get("author", []) if fields.get("author") else [],
                    repository=f"ebi_{database}",
                    dataset_type=dataset_type,
                    size_mb=None,
                    format=self._get_format_for_database(database),
                    license="Various",
                    access_url=f"https://www.ebi.ac.uk/{database}/{entry.get('id', '')}",
                    doi=fields.get("doi", [""])[0] if fields.get("doi") else None,
                    keywords=fields.get("keywords", []) if fields.get("keywords") else [],
                    last_updated=None,
                    download_count=None,
                    citation_count=None,
                    metadata={
                        "database": database,
                        "organism": fields.get("organism", []) if fields.get("organism") else [],
                        "study_type": fields.get("study_type", []) if fields.get("study_type") else []
                    }
                )
                
                datasets.append(dataset)
                
            except Exception as e:
                logging.warning(f"Error parsing EBI entry: {e}")
                continue
        
        return datasets
    
    def _determine_dataset_type(self, database: str, fields: Dict[str, Any]) -> DatasetType:
        """Determine dataset type based on database and fields"""
        if database == "pride":
            return DatasetType.EXPERIMENTAL  # Proteomics
        elif database == "arrayexpress":
            return DatasetType.GENOMIC  # Gene expression
        elif database == "ena":
            return DatasetType.GENOMIC  # Nucleotide sequences
        elif database == "chembl":
            return DatasetType.NUMERICAL  # Chemical data
        else:
            return DatasetType.MIXED
    
    def _get_format_for_database(self, database: str) -> List[str]:
        """Get expected formats for database"""
        format_map = {
            "pride": ["mzML", "mzXML", "RAW"],
            "arrayexpress": ["CEL", "TXT", "ADF"],
            "ena": ["FASTQ", "FASTA", "SRA"],
            "chembl": ["SDF", "CSV", "JSON"]
        }
        return format_map.get(database, ["Unknown"])
    
    async def close(self):
        if self.session:
            await self.session.close()


class GovernmentDataAPI:
    """Government research database access"""
    
    def __init__(self):
        self.apis = {
            "nih_data": {
                "base_url": "https://datascience.nih.gov/api",
                "search_endpoint": "/search"
            },
            "data_gov": {
                "base_url": "https://catalog.data.gov/api/3/action",
                "search_endpoint": "/package_search"
            },
            "eu_data": {
                "base_url": "https://data.europa.eu/api/hub/search",
                "search_endpoint": "/packages"
            }
        }
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            headers = {
                "User-Agent": "BachResearchAI/1.0 (mailto:research@example.com)"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def search_government_data(self, query: str, sources: Optional[List[str]] = None,
                                   limit: int = 100) -> Dict[str, List[DatasetInfo]]:
        """Search government research databases"""
        if sources is None:
            sources = ["data_gov", "eu_data"]
        
        results = {}
        
        for source in sources:
            try:
                if source == "data_gov":
                    datasets = await self._search_data_gov(query, limit)
                elif source == "eu_data":
                    datasets = await self._search_eu_data(query, limit)
                else:
                    datasets = []
                
                results[source] = datasets
                
            except Exception as e:
                logging.error(f"Error searching {source}: {e}")
                results[source] = []
        
        return results
    
    async def _search_data_gov(self, query: str, limit: int) -> List[DatasetInfo]:
        """Search data.gov"""
        session = await self._get_session()
        
        params = {
            "q": query,
            "rows": min(limit, 1000),
            "sort": "score desc"
        }
        
        async with session.get("https://catalog.data.gov/api/3/action/package_search", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_data_gov(data)
            else:
                return []
    
    async def _search_eu_data(self, query: str, limit: int) -> List[DatasetInfo]:
        """Search EU Open Data Portal"""
        session = await self._get_session()
        
        params = {
            "q": query,
            "limit": min(limit, 1000),
            "sort": "relevance desc"
        }
        
        async with session.get("https://data.europa.eu/api/hub/search/packages", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_eu_data(data)
            else:
                return []
    
    def _parse_data_gov(self, data: Dict[str, Any]) -> List[DatasetInfo]:
        """Parse data.gov response"""
        datasets = []
        
        for package in data.get("result", {}).get("results", []):
            try:
                dataset = DatasetInfo(
                    id=package.get("id", ""),
                    title=package.get("title", "Unknown"),
                    description=package.get("notes", ""),
                    authors=[package.get("author", "Unknown")],
                    repository="data_gov",
                    dataset_type=DatasetType.MIXED,
                    size_mb=None,
                    format=[resource.get("format", "Unknown") for resource in package.get("resources", [])],
                    license=package.get("license_title", "Unknown"),
                    access_url=f"https://catalog.data.gov/dataset/{package.get('name', '')}",
                    doi=None,
                    keywords=[tag.get("name", "") for tag in package.get("tags", [])],
                    last_updated=datetime.fromisoformat(package.get("metadata_modified", "1970-01-01T00:00:00").replace("Z", "+00:00")) if package.get("metadata_modified") else None,
                    download_count=None,
                    citation_count=None,
                    metadata={
                        "organization": package.get("organization", {}).get("title", ""),
                        "resources_count": len(package.get("resources", [])),
                        "groups": [group.get("title", "") for group in package.get("groups", [])]
                    }
                )
                
                datasets.append(dataset)
                
            except Exception as e:
                logging.warning(f"Error parsing data.gov entry: {e}")
                continue
        
        return datasets
    
    def _parse_eu_data(self, data: Dict[str, Any]) -> List[DatasetInfo]:
        """Parse EU Open Data response"""
        datasets = []
        
        for package in data.get("result", {}).get("results", []):
            try:
                dataset = DatasetInfo(
                    id=package.get("id", ""),
                    title=package.get("title", "Unknown"),
                    description=package.get("notes", ""),
                    authors=[package.get("author", "Unknown")],
                    repository="eu_data",
                    dataset_type=DatasetType.MIXED,
                    size_mb=None,
                    format=[resource.get("format", "Unknown") for resource in package.get("resources", [])],
                    license=package.get("license_title", "Various"),
                    access_url=f"https://data.europa.eu/data/datasets/{package.get('name', '')}",
                    doi=None,
                    keywords=[tag.get("name", "") for tag in package.get("tags", [])],
                    last_updated=datetime.fromisoformat(package.get("metadata_modified", "1970-01-01T00:00:00").replace("Z", "+00:00")) if package.get("metadata_modified") else None,
                    download_count=None,
                    citation_count=None,
                    metadata={
                        "country": package.get("country", ""),
                        "language": package.get("language", []),
                        "theme": package.get("theme", [])
                    }
                )
                
                datasets.append(dataset)
                
            except Exception as e:
                logging.warning(f"Error parsing EU data entry: {e}")
                continue
        
        return datasets
    
    async def close(self):
        if self.session:
            await self.session.close()


class RemoteDatasetManager:
    """Unified manager for all remote dataset searches"""
    
    def __init__(self):
        self.ncbi = NCBIDatasetAPI()
        self.ebi = EBIDatasetAPI()
        self.government = GovernmentDataAPI()
    
    async def search_all_datasets(self, query: str, dataset_types: Optional[List[DatasetType]] = None,
                                repositories: Optional[List[str]] = None,
                                limit_per_repo: int = 50) -> Dict[str, List[DatasetInfo]]:
        """Search all available remote datasets"""
        
        results = {}
        search_tasks = []
        
        # NCBI searches
        if not repositories or "ncbi_genomes" in repositories:
            task = asyncio.create_task(self.ncbi.search_genomes(query, limit_per_repo))
            search_tasks.append(("ncbi_genomes", task))
        
        if not repositories or "ncbi_sra" in repositories:
            task = asyncio.create_task(self.ncbi.search_sra(query, limit_per_repo))
            search_tasks.append(("ncbi_sra", task))
        
        # EBI searches
        if not repositories or any(db in repositories for db in ["ebi_pride", "ebi_arrayexpress", "ebi_ena", "ebi_chembl"]):
            ebi_dbs = ["pride", "arrayexpress", "ena", "chembl"]
            if repositories:
                ebi_dbs = [db.replace("ebi_", "") for db in repositories if db.startswith("ebi_")]
            
            task = asyncio.create_task(self.ebi.search_datasets(query, ebi_dbs, limit_per_repo))
            search_tasks.append(("ebi", task))
        
        # Government data searches
        if not repositories or any(source in repositories for source in ["data_gov", "eu_data"]):
            gov_sources = ["data_gov", "eu_data"]
            if repositories:
                gov_sources = [source for source in repositories if source in gov_sources]
            
            task = asyncio.create_task(self.government.search_government_data(query, gov_sources, limit_per_repo))
            search_tasks.append(("government", task))
        
        # Execute all searches
        for repo_name, task in search_tasks:
            try:
                result = await task
                
                if repo_name == "government":
                    # Government returns dict of sources
                    for source, datasets in result.items():
                        results[source] = datasets
                elif repo_name == "ebi":
                    # EBI returns list
                    results["ebi"] = result
                else:
                    # NCBI returns list
                    results[repo_name] = result
                    
            except Exception as e:
                logging.error(f"Search failed for {repo_name}: {e}")
                if repo_name == "government":
                    results.update({"data_gov": [], "eu_data": []})
                else:
                    results[repo_name] = []
        
        # Filter by dataset type if specified
        if dataset_types:
            for repo in results:
                results[repo] = [
                    dataset for dataset in results[repo]
                    if dataset.dataset_type in dataset_types
                ]
        
        return results
    
    async def search_by_domain(self, query: str, domain: str, limit: int = 100) -> List[DatasetInfo]:
        """Search datasets by scientific domain"""
        domain_mapping = {
            "genomics": ["ncbi_genomes", "ncbi_sra", "ebi_ena"],
            "proteomics": ["ebi_pride"],
            "transcriptomics": ["ebi_arrayexpress"],
            "chemistry": ["ebi_chembl"],
            "clinical": ["data_gov"],
            "environmental": ["data_gov", "eu_data"],
            "social": ["data_gov", "eu_data"]
        }
        
        repositories = domain_mapping.get(domain.lower(), [])
        if not repositories:
            # Search all if domain not recognized
            repositories = None
        
        results = await self.search_all_datasets(query, repositories=repositories, limit_per_repo=limit)
        
        # Flatten results
        all_datasets = []
        for repo_datasets in results.values():
            all_datasets.extend(repo_datasets)
        
        return all_datasets
    
    async def get_repository_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available repositories"""
        return {
            "ncbi_genomes": {
                "name": "NCBI Genomes",
                "description": "Genome assemblies and annotations",
                "types": ["genomic"],
                "url": "https://www.ncbi.nlm.nih.gov/datasets/genome/"
            },
            "ncbi_sra": {
                "name": "NCBI Sequence Read Archive",
                "description": "Raw sequencing data",
                "types": ["genomic"],
                "url": "https://www.ncbi.nlm.nih.gov/sra"
            },
            "ebi_pride": {
                "name": "PRIDE Archive",
                "description": "Proteomics data",
                "types": ["experimental"],
                "url": "https://www.ebi.ac.uk/pride/"
            },
            "ebi_arrayexpress": {
                "name": "ArrayExpress",
                "description": "Gene expression data",
                "types": ["genomic"],
                "url": "https://www.ebi.ac.uk/arrayexpress/"
            },
            "ebi_ena": {
                "name": "European Nucleotide Archive",
                "description": "Nucleotide sequence data",
                "types": ["genomic"],
                "url": "https://www.ebi.ac.uk/ena"
            },
            "ebi_chembl": {
                "name": "ChEMBL",
                "description": "Bioactive drug-like compounds",
                "types": ["numerical"],
                "url": "https://www.ebi.ac.uk/chembl/"
            },
            "data_gov": {
                "name": "Data.gov",
                "description": "US government research data",
                "types": ["mixed"],
                "url": "https://catalog.data.gov/"
            },
            "eu_data": {
                "name": "EU Open Data Portal",
                "description": "European government data",
                "types": ["mixed"],
                "url": "https://data.europa.eu/"
            }
        }
    
    async def close(self):
        """Close all connections"""
        await self.ncbi.close()
        await self.ebi.close()
        await self.government.close()


# Convenience functions for Bach commands
async def search_remote_datasets(query: str, domain: Optional[str] = None,
                                dataset_types: Optional[List[str]] = None,
                                repositories: Optional[List[str]] = None,
                                max_results: int = 200) -> Dict[str, List[DatasetInfo]]:
    """Search remote scientific datasets"""
    manager = RemoteDatasetManager()
    
    try:
        # Convert string types to enum if provided
        type_enums = None
        if dataset_types:
            type_enums = [DatasetType(dt) for dt in dataset_types if dt in [e.value for e in DatasetType]]
        
        if domain:
            results = await manager.search_by_domain(query, domain, max_results)
            return {"domain_search": results}
        else:
            results = await manager.search_all_datasets(
                query, 
                dataset_types=type_enums,
                repositories=repositories,
                limit_per_repo=max_results // 4  # Distribute across repos
            )
            return results
            
    finally:
        await manager.close()


async def get_dataset_repositories() -> Dict[str, Dict[str, Any]]:
    """Get available dataset repositories"""
    manager = RemoteDatasetManager()
    try:
        return await manager.get_repository_info()
    finally:
        await manager.close()


if __name__ == "__main__":
    async def main():
        # Example: Search for COVID-19 datasets
        print("Searching for COVID-19 datasets...")
        results = await search_remote_datasets(
            "COVID-19",
            domain="genomics",
            max_results=20
        )
        
        print(f"Found datasets:")
        for repo, datasets in results.items():
            print(f"  {repo}: {len(datasets)} datasets")
            for dataset in datasets[:3]:  # Show first 3
                print(f"    - {dataset.title} ({dataset.repository})")
        
        # Show available repositories
        print("\nAvailable repositories:")
        repos = await get_dataset_repositories()
        for repo_id, info in repos.items():
            print(f"  {repo_id}: {info['name']} - {info['description']}")
    
    asyncio.run(main())