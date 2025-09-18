from copy import deepcopy
from math import floor
from typing import Dict

from .labels import clean_up as clean_up_labels


def clean_up(data: Dict) -> Dict :
    cleaned = deepcopy(data)

    annotations = cleaned.get('annotations', [])

    for annotation in annotations:
        del annotation["uid"]
        annotation["labels"] = clean_up_labels(annotation["labels"])
    
    return cleaned
