import base64
from math import floor
from typing import Dict

try:
    import cv2  # type: ignore
    import numpy as np
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
        "OpenCV and Numpy are required to use the mask helpers. To install them,"
        " run: pip install isahitlab[image]."
    ) from err

from .annotation import clean_up
from .color import to_bgr
from .labels import extract_main_labels
from .points import denormalize_points, vertices_to_points, points_to_vertices, bbox_to_corners


def polygon_data_to_segmentation_data(data: Dict, labels_mapping_by_id : Dict[str, Dict], image_size : Dict[str, int]) -> Dict :
    
    data = clean_up(data)

    segmentation_task = {
        **data,
        "annotations": [],
        "image" : image_size 
    }

    mask = np.zeros((image_size["height"], image_size["width"], 3))

    annotations = data.get('annotations', [])

    instance_id = 2

    for annotation in annotations:
        polygons = annotation.get("polygons", [])
        if len(polygons) == 0:
            continue

        # Resolve B Channel
        labels = annotation["labels"] if "labels" in annotation else {}
        main_labels = extract_main_labels(labels)
    
        matching_label_in_target = labels_mapping_by_id.get(main_labels[0]['id'], None) if len(main_labels) > 0 else None
        
        r = instance_id % 256
        g = floor(instance_id / 256)
        if matching_label_in_target:
            b = matching_label_in_target["bChannel"]
        else:
            b = 1
        rgb = (r, g, b)

        # Handle polygons
        cv_polygons = []
        for polygon in polygons:
            normalized_vertices =  polygon["geometry"]["vertices"]
            geometry_type = polygon["geometry"]["type"]

            if geometry_type == "rectangle":
                normalized_vertices = bbox_to_corners(normalized_vertices)

            polygon["color"] = matching_label_in_target.get("color", polygon["color"]) if matching_label_in_target else polygon["color"]
            denormalized_points = denormalize_points(vertices_to_points(normalized_vertices), image_size, 0)
            
            # Approximation are denormalized in the lab
            polygon["geometry"]["vertices"] = points_to_vertices(denormalized_points)
            polygon["geometry"]["type"] = "polygon"

            cv_polygon = np.array([(point['x'], point['y'])
                               for point in denormalized_points], dtype=np.int32)
            cv_polygons.append(cv_polygon)
            
        cv2.fillPoly(mask, cv_polygons, to_bgr(rgb))

        # Create annotation
        segmentation_task["annotations"].append({
            **annotation,
            "color" : matching_label_in_target.get("color", annotation["color"]) if matching_label_in_target else annotation["color"],
            "polygons": list(rgb),
            "approximation" : {
                "polygons": polygons,
                "minus" : []
            }
        })

        instance_id += 1

    # Mask to base64
    retval, buffer = cv2.imencode('.png', mask)
    jpg_as_text = base64.b64encode(buffer)
    base64mask = 'data:image/png;base64,' + jpg_as_text.decode()
    segmentation_task["mask"] = base64mask
    return segmentation_task
