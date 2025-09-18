"""Methods to handle labels formatting

KILI example

"categories": [
    {
        "name": "PARENT"
    }
],
"children": {
    "CLASSIFICATION_JOB": {
        "categories": [
            {
                "confidence": 100,
                "name": "ENFANT_1"
            }
        ]
    },
    "CLASSIFICATION_JOB_0": {
        "categories": [
            {
                "children": {
                    "TRANSCRIPTION_JOB_0": {
                        "text": "test 2"
                    }
                },
                "confidence": 100,
                "name": "ENFANT_2"
            },
            {
                "children": {
                    "TRANSCRIPTION_JOB": {
                        "text": "test"
                    }
                },
                "confidence": 100,
                "name": "ENFANT_1"
            }
        ]
    }
},

"""

from copy import deepcopy
from typing import Dict, List, Optional


def clean_up(labels : Dict):
    cleaned = deepcopy(labels)
    for list_id in cleaned:
        for label in cleaned[list_id]["labels"]:
            del label["uid"]
        if cleaned[list_id].get("children", None):
            cleaned[list_id]["children"] = clean_up(cleaned[list_id]["children"])
    return cleaned

def extract_main_labels(labels : Dict) -> List[Dict] :
    main_labels = []
    for list in labels:
        value = labels[list]
        for label in value['labels']:
            main_labels.append({
                "id" : label["id"],
                "name" : label["id"],
                "list" : list
            })
    
    return main_labels

def find_label_in_main_list(label_id : str, project_configuration : Dict) -> List[Dict] :
    mainLists = project_configuration["metadata"]["labelOptions"]["mainLists"]
    availableLabels = project_configuration["metadata"]["labelOptions"]["availableLabels"]
    for mlist in mainLists:
        mainListKey = mlist["name"]
        for datalistKey in mlist["keys"]:
            for label in availableLabels.get(datalistKey, []):
                if label["id"] == label_id:
                    return {
                        mainListKey : {
                            "labels" : [
                                {
                                    "id": label["id"],
                                    "name": label["name"]
                                }
                            ]
                        }
                    }
    return None

def flatten_available_labels_used_in_main_lists(project_configuration : Dict, label_attr : str = 'id') -> List[Dict] :
    mainLists = project_configuration["metadata"]["labelOptions"]["mainLists"]
    availableLabels = project_configuration["metadata"]["labelOptions"]["availableLabels"]
    labels_list = list()
    for mlist in mainLists:
        for datalistKey in mlist["keys"]:
            for label in availableLabels.get(datalistKey, []):
                labels_list.append(label[label_attr])
                
    return labels_list

def extract_labels_map_by_id(project_configuration : Dict, field: Optional[str] = None) -> List[Dict] :
    availableLabels = project_configuration.get("metadata",{}).get("labelOptions", {}).get("availableLabels",{})

    mapping = {}

    for listId in availableLabels:
        for label in availableLabels[listId]:
            if field:
                mapping[label['id']] = label[field]
            else:
                mapping[label['id']] = label
    
    return mapping