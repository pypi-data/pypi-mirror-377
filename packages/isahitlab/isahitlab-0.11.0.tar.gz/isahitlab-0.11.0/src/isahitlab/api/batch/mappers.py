""" Domain Filter to API params"""
from isahitlab.domain.batch import BatchFilters

def batch_filters_mapper(filters: BatchFilters):
    params = {
        "pagination" : "false" if filters.pagination == False else "true",
        "page" : filters.page,
        "limit" : filters.limit,
        "projectId" : filters.project_id,
    }

    if filters.status_in and len(filters.status_in):
        params['statuses'] = filters.status_in

    if filters.search and len(filters.search):
        params['search'] = filters.search

    return params