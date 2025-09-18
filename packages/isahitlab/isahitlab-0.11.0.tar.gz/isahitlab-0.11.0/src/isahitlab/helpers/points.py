from typing import Dict, List


def bbox_to_corners(bbox: List[float]) -> List[float]:
    """ Transform a list of point representing a bbox to the four points of a rectangle"""

    [top_left_x, top_left_y, bottom_right_x, bottom_right_y] = bbox

    return [
        top_left_x,
        top_left_y,
        bottom_right_x,
        top_left_y,
        bottom_right_x,
        bottom_right_y,
        top_left_x,
        bottom_right_y
    ]

def bbox_to_center_and_size(bbox: List[float]) -> List[float]:
    """ Transform a list of point representing a bbox to the center x and y with width and height"""

    [top_left_x, top_left_y, bottom_right_x, bottom_right_y] = bbox

    min_x = min(top_left_x, bottom_right_x)
    max_x = max(top_left_x, bottom_right_x)
    min_y = min(top_left_y, bottom_right_y)
    max_y = max(top_left_y, bottom_right_y)

    width = max_x - min_x
    height = max_y - min_y
    center_x = min_x + (width) / 2
    center_y = min_y + (height) / 2

    return [
        center_x,
        center_y,
        width,
        height
    ]

def corners_to_bbox(vertices: List[float]) -> List[float]:
    """ Transform a list of point representing a bbox to the four points of a rectangle"""

    [a_x, a_y, b_x, b_y, c_x, c_y, d_x, d_y] = vertices

    
    min_x = min(a_x, b_x, c_x, d_x)
    max_x = max(a_x, b_x, c_x, d_x)
    min_y = min(a_y, b_y, c_y, d_y)
    max_y = max(a_y, b_y, c_y, d_y)

    return [
        min_x,
        min_y,
        max_x,
        max_y
    ]

def vertices_to_points(vertices: List[float]) -> List[Dict]:
    """Transform vertices [float,float,float,float,...] to points [{ x: float, y: float },{ x: float, y: float },...]"""

    points = []

    for i, v in enumerate(vertices):
        if i % 2 == 0:
            points.append({ "x" : vertices[i], "y" : vertices[i + 1]})

    return points

def points_to_vertices(points):
    """Transform points [{ x: float, y: float },{ x: float, y: float },...] to vertices [float,float,float,float,...] """
    vertices = []
    for p in points:
        vertices.append(p['x'])
        vertices.append(p['y'])
    return vertices

def denormalize_points(points: List[Dict], dimension : Dict, round_decimal : int = None) -> List[float]:
    """Transform relative points to absolute points"""

    denormalized_points = []

    for p in points:
        x = p['x'] * float(dimension['width'])
        y = p['y'] * float(dimension['height'])
        if round_decimal != None:
            x = round(x, round_decimal)
            y = round(y, round_decimal)
        denormalized_points.append({"x" : x, "y": y})

    return denormalized_points

def normalize_points(points: List[Dict], dimension : Dict, round_decimal : int = None) -> List[float]:
    """Transform relative points to absolute points"""

    normalized_points = []

    for p in points:
        x = p['x'] / float(dimension['width'])
        y = p['y'] / float(dimension['height'])
        if round_decimal != None:
            x = round(x, round_decimal)
            y = round(y, round_decimal)
        normalized_points.append({"x" : x, "y": y})

    return normalized_points