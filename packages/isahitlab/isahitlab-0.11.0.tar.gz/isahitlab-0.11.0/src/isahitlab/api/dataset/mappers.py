""" Domain Filter to API params"""
from isahitlab.domain.dataset import DatasetBrowsingFilters

def dataset_browsing_filters_mapper(filters: DatasetBrowsingFilters):
    params = {}

    if filters.folder:
        params['folder'] = filters.folder

    if filters.next_token and len(filters.next_token):
        params['nextToken'] = filters.next_token
        
    return params