from typing import Dict, Optional


def merge_data_and_metadata(data_body: Optional[Dict], metadata_body : Optional[Dict]):
    data_body = data_body or {}
    metadata_body = metadata_body or {}

    keys = set([*data_body.keys(),*metadata_body.keys()])

    merged = {}

    for key in keys:
        value_in_data = data_body.get(key, None)
        value_in_metadata = metadata_body.get(key, None)
    
        if value_in_data and value_in_metadata and isinstance(value_in_data, dict) and isinstance(value_in_metadata, dict):
          merged[key] = {
            **value_in_metadata,
            **value_in_data
          }
        elif value_in_data != None:
          merged[key] = value_in_data
        elif value_in_metadata != None:
          merged[key] = value_in_metadata

    return merged