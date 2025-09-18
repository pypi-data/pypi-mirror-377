import json
import logging
import pathlib
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Union

from isahitlab.domain.project import ProjectType
from isahitlab.helpers.labels import extract_main_labels
from isahitlab.helpers.path import check_extension
from isahitlab.helpers.points import (bbox_to_corners, denormalize_points,
                                      normalize_points, vertices_to_points)

from .base import BaseFormatter

logger = logging.getLogger(__name__)

class LabToKiliFormatter(BaseFormatter):
    """Formatter used to ensure retrocompatibilty with kili"""

    is_sequence: bool = False

    export : List[Dict[str, Any]]= None

    def __init__(self, project_configuration : Dict, options : Dict = {}) -> None :

        self._init_configuration(project_configuration, options, {
            "compatible_types" : [
                "form.tool-iat-rectangle", 
                "iat-rectangle",
                "form.tool-iat-polygon", 
                "iat-polygon",
                "form.tool-iat-polyline", 
                "iat-polyline",
                "form.tool-iat-graph", 
                "iat-graph",
                "form.tool-iat-segmentation", 
                "iat-segmentation"
            ]
        })
        
        # Check output filename
        if options.get("output_filename", None) and not check_extension(options.get("output_filename", ""), ".json"):
            raise Exception('"output_filename" must have .json extension')
        
        self.is_sequence = self._project_configuration.get("metadata", {}).get("toolOptions", {}).get("sequence", False)
        

    ### Transform

    def format_tasks(self, tasks: List[Dict]) -> List[Dict]:
        formatted_tasks = []

        for task in tasks:
            formatted_task = self._format_task(task)
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    
    ### Export

    def _init_export(self):
        self.export = []
    
    def append_task_to_export(self, task: Dict):
        if self.export == None:
            self._init_export()

        self.export.append(self._format_task(task))

    def complete_export(self):
        if self.export == None:
            logger.warning('Nothing to export')
            return
        
        if self._options.get("in_memory"):
            return self.export
        
        now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        default_folder = '.'
        extra_filename_part = "_{}".format(self._options.get("extra_filename_part")) if "extra_filename_part" in self._options else ""
        default_filename = f'lab_kili{extra_filename_part}_{now_str}.json'
        output_path = pathlib.Path(self._options["output_folder"] or default_folder)
        export_name = self._options["output_filename"] or default_filename

        outputfile_path = output_path / export_name
        outputfile_path.parent.mkdir(parents=True, exist_ok=True)

        with outputfile_path.open('w') as ef:
            json.dump(self.export, ef, indent=2)

        print("Exported to \"{}\"".format(str(pathlib.Path(outputfile_path).absolute())))

    def _format_task(self, task : Dict) -> Dict:
        task = self._normalize_task(task)
        formatted_task = {
            "createdAt": task["createdAt"],
            "content": self._map_resources(task),
            "externalId": task["name"],
            "id": task["_id"],
            "isHoneypot": False,
            "jsonMetadata": {},
            "latestLabel": self._map_data(task),
            "resolution": self._map_image_size(task),
            "skipped": False,
            "status": self._map_status(task)
        }

        return formatted_task

    def _map_image_size(self, task: Dict) -> Union[Dict[str, int], None]:
        return task.get('data', {}).get('body', {}).get('image', None)

    def _map_status(self, task: Dict) -> Literal["TODO", "ONGOING", "LABELED", "REVIEWED", "TO_REVIEW"]:
        if task['status'] == 'complete':
            return 'LABELED'
        else:
            return 'TODO'


    def _map_resource(self, resource) -> Union[Dict, str]:
        if isinstance(resource, dict):
            return resource['name'] if 'name' in resource else resource['id']
        else:
            return resource

    def _map_resources(self, task: Dict) -> str:
        if "resources" in task and len(task["resources"]) > 0 :
            return ",".join([*map(lambda r : self._map_resource(r), task["resources"])])
        else:
            return ''

    def _map_data(self, task: Dict) -> Union[Dict, None]:
        if "data" not in task:
            return None
        
        data = task.get("data", None)

        if not data or len(data) == 0:
            return None

        return {
            "author": self._map_data_author(data),
            "createdAt": data['createdAt'],
            "isLatestLabelForUser": True,
            "isSentBackToQueue": False,
            "jsonResponse": self._map_data_body(task),
            "labelType": self._map_data_type(data),
            "modelName": None
        }
    
    def _map_data_author(self, data: Dict):
        """
        {
            "email": "julien.cachou.ext@veolia.com",
            "firstname": "Julien",
            "id": "clraqptja02zr087wdp9zeiu5",
            "lastname": "CACHOU",
            "name": "Julien CACHOU"
        }
        """

        if "user" not in data or not data["user"]:
            return None
        
        name = data['user']['name']

        name_parts = name.split(' ')
        firstname = name_parts[0] if len(name_parts) > 0 else name
        lastname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        return {
            "email" : data['user']['email'],
            "name" : name,
            "firstname" : firstname,
            "lastname" : lastname,
            "id" : data['user']['id']
        }
    
    def _map_data_type(self, data: Dict) -> str:
        if data['type'] == 'review':
            return "REVIEW"
        else: 
            return "DEFAULT" 

    def _map_data_body(self, task: Dict) -> Union[Dict, None] :
        data = task["data"]
        if "body" not in data:
            return None
        
        body : Dict = data["body"]
        project_type : ProjectType = data["projectType"]
        resources = task.get("resources", [])

        annotations = {}

        if project_type == 'iat-rectangle':
            annotations = self._format_polygon_annotations(body, "rectangle", sequence_number=len(resources) if self.is_sequence else None)
        elif project_type == 'iat-polygon':
            annotations = self._format_polygon_annotations(body, "polygon", sequence_number=len(resources) if self.is_sequence else None)
        elif project_type == 'iat-segmentation':
            annotations = self._format_segmentation_annotations(body)
        else:
            logging.warning('LAB To kili annotations formatting is not available for project type "{}"'.format(project_type))

        return { "OBJECT_DETECTION_JOB": { "annotations" : annotations } }
        
    def _format_polygon_annotations(self, body, type: str, sequence_number: Union[int, None] = None) -> Union[List[Dict], Dict[str, Dict]]:
        formatted_annotations_by_timestamp = {}
        annotations = body["annotations"] if "annotations" in body else []

        # Inititalize dict
        if sequence_number != None:
            for s in range(0, sequence_number):
                formatted_annotations_by_timestamp[s] = {}
        
        formatted_annotations_by_timestamp["none"] = {}


        if "image" not in body or not body["image"]:
            if len(annotations) > 0:
                logging.warning("Annotations ignored due to missing image size")
            return []


        image_size = body.get("image", None)

        for annotation in annotations:
            polygons = annotation["polygons"]
            labels = annotation["labels"] if "labels" in annotation else {}
            main_labels = extract_main_labels(labels)
            formatted_annotation = {
                "boundingPoly" : [],
                "categories" : [*map(lambda main_label : { "name" : main_label['id'] }, main_labels)],
                "children" : self._format_labels(labels, True),
                "type" : type
            }
            bounding_polys_by_timestamp = {}
            for polygon in polygons:
                vertices = polygon["geometry"]["vertices"]
                if type == "rectangle":
                    vertices = bbox_to_corners(vertices)
                timestamp = int(polygon.get('timestamp', 1)) - 1  if sequence_number != None else "none"
                if timestamp not in bounding_polys_by_timestamp:
                    bounding_polys_by_timestamp[timestamp] = []
                poly = self._format_vertices(vertices, image_size)
                bounding_polys_by_timestamp[timestamp].append(poly)

            for sequence in bounding_polys_by_timestamp:
                if len(formatted_annotations_by_timestamp[sequence]) == 0:
                    formatted_annotations_by_timestamp[sequence]["OBJECT_DETECTION_JOB"] = {
                        "annotations" : []
                    }
                formatted_annotations_by_timestamp[sequence]["OBJECT_DETECTION_JOB"]["annotations"].append({ **formatted_annotation, "boundingPoly" : bounding_polys_by_timestamp[sequence] })
        
        if sequence_number != None:
            del formatted_annotations_by_timestamp["none"]
            return formatted_annotations_by_timestamp
        else:            
            return formatted_annotations_by_timestamp["none"]

    
    def _format_segmentation_annotations(self, body) -> List[Dict]:
        formatted_annotations = []
        annotations = body["annotations"] if "annotations" in body else []
        
        if "image" not in body or not body["image"]:
            if len(annotations) > 0:
                logging.warning("Annotations ignored due to missing image size")
            return []


        image_size = body.get("image", None)

        for annotation in annotations:
            polygons = annotation.get('approximation',{}).get('polygons',[])
            minus_polygons = annotation.get('approximation',{}).get("minus", [])
            labels = annotation["labels"] if "labels" in annotation else {}
            main_labels = extract_main_labels(labels)
            formatted_annotation = {
                "categories" : [*map(lambda main_label : { "name" : main_label['id'] }, main_labels)],
                "children" : self._format_labels(labels, children_only=True),
                "type" : "semantic",
                "mid" : str(uuid.uuid4()).replace('-', '')[0:15]
            }

            # Prepare minus boxes
            formatted_minus = []
            for polygon in minus_polygons:
                vertices = polygon["geometry"]["vertices"]
                formatted_minus.append(self._format_vertices(vertices, image_size, denormalized=True))

            for pindex, polygon in enumerate(polygons):
                vertices = polygon["geometry"]["vertices"]
                poly = self._format_vertices(vertices, image_size, denormalized=True)
                formatted_annotations.append({
                    "boundingPoly" : [
                        poly, 
                        *(formatted_minus if pindex == 0 else [])], # We add minus polygons in the first "annotation" only
                    **formatted_annotation
                })

        return formatted_annotations
    

    def _format_vertices(self, vertices : List[Union[float, int]], image_size : Dict[str, int], denormalized : bool = False):
        if denormalized:
            denormalized_points = vertices_to_points(vertices)
            normalized_points = normalize_points(denormalized_points, image_size)
        else:
            normalized_points = vertices_to_points(vertices)
            denormalized_points = denormalize_points(normalized_points, image_size, 2)
        return {
            "normalizedVertices" : normalized_points,
            "vertices" : denormalized_points
        }

    def _format_labels(self, labels : Dict, children_only : bool = False):
        children = {}
        for list in labels:
            if not children_only:
                children[list] = {
                    "categories" : [ { "name" : l["id"] } for l in (labels[list].get("labels", []) or [])],
                }
            if "children" in labels[list] and len(labels[list]["children"]):
                formatted_children = self._format_labels(labels[list]["children"])
                children = { **children, **formatted_children }
                
        return children
    

    def prepare_import(self, tasks: List[Dict]):
        raise NotImplementedError