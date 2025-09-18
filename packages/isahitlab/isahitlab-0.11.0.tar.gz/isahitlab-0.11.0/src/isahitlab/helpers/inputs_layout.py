from typing import Any, Dict, List, NewType

InputsLayout = NewType("InputsLayout", List[List[List[Dict[str,Any]]]])

IAT_INPUT_TYPES = [
    "tool-iat-rectangle", 
    "tool-iat-polygon", 
    "tool-iat-polyline",
    "tool-iat-graph",
    "tool-iat-segmentation", 
]

def extract_all_inputs_from_layout(layout: InputsLayout) -> List[Dict[str, Any]]:
    """Extract the inputs from the layouts"""
    inputs: List[Dict[str,Dict]] = []

    for row in layout:
        for col in row:
            for input in col:
                inputs.append(input)

    return inputs

def extract_not_static_inputs_from_layout(layout: InputsLayout) -> List[Dict[str, Any]]:
    """Extract from the layouts only the inputs that can be set for task initialization"""
    inputs: List[Dict[str,Dict]] = []

    for row in layout:
        for col in row:
            for input in col:
                if input['submit'] != False or not input.get('static', False):
                    inputs.append(input)

    return inputs

def extract_inputs_by_types_from_layout(layout: InputsLayout, types: List[str]) -> List[Dict[str, Any]]:
    """Extract from the layouts only the inputs with the provided type"""
    inputs: List[Dict[str,Dict]] = []

    for row in layout:
        for col in row:
            for input in col:
                if input['type'] in types:
                    inputs.append(input)

    return inputs

def extract_inputs_iat_from_layout(layout: InputsLayout):
    """Extract from the layouts only the inputs with the provided type"""
    inputs: List[Dict[str,Dict]] = []

    for row in layout:
        for col in row:
            for input in col:
                if input['type'][0:8] == "tool-iat":
                    inputs.append(input)

    return inputs

def extract_inputs_by_id_from_layout(layout: InputsLayout, id: str) -> List[Dict[str, Any]]:
    """Extract from the layouts only the input with the id"""
    inputs: List[Dict[str,Dict]] = []

    for row in layout:
        for col in row:
            for input in col:
                if input['id'] == id:
                    inputs.append(input)

    return inputs