"""
Bach API Utils Package  
Enhanced API integrations for scientific databases and remote datasets
"""

from .enhanced_api import (
    EnhancedAPIManager,
    enhanced_search,
    search_with_datasets
)

from .remote_datasets import (
    RemoteDatasetManager,
    DatasetInfo,
    DatasetType,
    NCBIDatasetAPI,
    EBIDatasetAPI,
    GovernmentDataAPI,
    search_remote_datasets,
    get_dataset_repositories
)

__all__ = [
    'EnhancedAPIManager',
    'RemoteDatasetManager',
    'DatasetInfo', 
    'DatasetType',
    'NCBIDatasetAPI',
    'EBIDatasetAPI',
    'GovernmentDataAPI',
    'enhanced_search',
    'search_with_datasets',
    'search_remote_datasets',
    'get_dataset_repositories'
]