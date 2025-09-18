""" Domain Filter to API params"""
from isahitlab.domain.integration import IntegrationFilters

def integration_filters_mapper(filters: IntegrationFilters):
    params = {
        "pagination" : "false" if filters.pagination == False else "true",
        "page" : filters.page,
        "limit" : filters.limit
    }

    if filters.visibility_in and len(filters.visibility_in):
        params['visibility'] = filters.visibility_in

    if filters.search and len(filters.search):
        params['search'] = filters.search
        
    return params