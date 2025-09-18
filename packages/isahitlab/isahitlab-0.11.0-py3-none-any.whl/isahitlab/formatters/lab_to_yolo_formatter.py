import logging
import pathlib
import shutil
import tempfile
from datetime import datetime
from typing import Any, Dict, List

from isahitlab.helpers.labels import (
  extract_main_labels, flatten_available_labels_used_in_main_lists)
from isahitlab.helpers.path import check_extension
from isahitlab.helpers.points import (bbox_to_center_and_size,
                                      normalize_points, points_to_vertices,
                                      vertices_to_points)

from .base import BaseFormatter

logger = logging.getLogger(__name__)

class LabToYoloFormatter(BaseFormatter):
    """Formatter to export tasks to Yolo (v8) format 
    
    **archive.zip**

    - data.yaml
    - labels/
        - image1.jpg.txt
        - image2.jpg.txt
    
    **data.yaml**
    
    nc: 2
    names: ['label_1', 'label_2']
    
    **image1.jpg.txt**

    0 0.6545064391681276 0.4235482071561457 0.0797404071439336 0.18190535356334903
    0 0.3622486209742762 0.3927660911752291 0.07606270256677716 0.15973167539023203
    1 0.34460042208424047 0.5709931135225523 0.06213055937206563 0.1554331519686042
    2 0.3407572947004013 0.49469991805078334 0.028823455378793328 0.03700789332585808
    3 0.39520159930478876 0.5274376698390424 0.025620849225594045 0.04099335876095056
    3 0.38068257272515843 0.47885714285714287 0.060650859736031015 0.09142857142857141

    **For rectangle:**     
    <class> <x_center> <y_center> <width> <height>

    **For polygon:**
    <class> <x> <y> <x> <y> <x> <y> ...  <x> <y>

    https://yolov8.org/yolov8-label-format/

    """
    classes : List[Dict[str, Any]]= None
    temp_dir : tempfile.TemporaryDirectory = None
    is_segmentation: bool = False

    def __init__(self, project_configuration : Dict, options : Dict = {}) -> None :
        
        if options.get("in_memory", None):
            raise Exception('"in_memory" not supported')
        
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

        # Check if is sequence
        if self._project_configuration.get("metadata", {}).get("toolOptions", {}).get("sequence", False):
            raise Exception('LabToYoloFormatter does not support sequences')

        # Check output filename
        if options.get("output_filename", None) and not check_extension(options.get("output_filename", ""), ".zip"):
            raise Exception('"output_filename" must have .zip extension')

        self.is_segmentation = self._type == "iat-segmentation" or self._type == "tool-iat-segmentation"
    
    ### Transform

    def format_tasks(self, tasks: List[Dict]) -> List[Dict]:
        formatted_tasks = []

        for task in tasks:
            formatted_task = self._format_task(task)
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    
    ### Export

    def _init_export(self):
        self.classes = flatten_available_labels_used_in_main_lists(self._project_configuration)
        self.temp_dir = tempfile.TemporaryDirectory()

    def append_task_to_export(self, task: Dict):
        if self.temp_dir == None:
            self._init_export()

        rows = self._format_task(task)
        task_name = task["name"]
        self._write_labels_file(task_name, rows)

    def complete_export(self):
        if self.temp_dir == None:
            logger.warning('Nothing to export')
            return
        
        self._write_classes_file()
        now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        default_folder = '.'
        extra_filename_part = "_{}".format(self._options.get("extra_filename_part")) if "extra_filename_part" in self._options else ""
        default_filename = f'lab_yolo{extra_filename_part}_{now_str}.zip'
        output_folder = self._options.get("output_folder", None) or default_folder
        outputfile_path = "{}/{}".format(output_folder, self._options.get("output_filename", None) or default_filename)

        self._make_archive(outputfile_path)

        self.temp_dir.cleanup()

        print("Exported to \"{}\"".format(str(pathlib.Path(outputfile_path).absolute())))

    def _format_task(self, task : Dict) -> Dict:
        task = self._normalize_task(task)
        rows = []
        annotations = task.get("data", {}).get("body", {}).get("annotations", [])
        image_size = task.get("data", {}).get("body", {}).get("image", None)
        
        for annotation in annotations:
            if self.is_segmentation:
                polygons = annotation.get('approximation',{}).get('polygons',[])
            else:
                polygons = annotation["polygons"]
            labels = annotation["labels"] if "labels" in annotation else {}
            main_labels = extract_main_labels(labels)
            #select first label
            label = main_labels[0] if len(main_labels) > 0 else None
            label_index = self.classes.index(label['id']) if label else -1
            
            for polygon in polygons:
                if self.is_segmentation and image_size: 
                    vertices = points_to_vertices(normalize_points(vertices_to_points(polygon["geometry"]["vertices"]), image_size))
                else:
                    vertices = polygon["geometry"]["vertices"]
                if polygon["geometry"]["type"] == "rectangle":
                    vertices = bbox_to_center_and_size(vertices)
                rows.append([label_index, *vertices])

        return rows


    def _make_archive(self, output_filename: str) -> str:
        """Make the export archive."""
        path_folder = pathlib.Path(self.temp_dir.name)
        path_archive = shutil.make_archive(str(path_folder), "zip", path_folder)

        output_path = pathlib.Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(path_archive, output_path)
        return str(output_path)


    def _write_classes_file(self):
        file_path = pathlib.Path(self.temp_dir.name) / "data.yaml"
        with file_path.open("wb") as fout:
            categories_str = ",".join([*map(lambda c : f"'{c}'", self.classes)])
            fout.write(f"nc: {len(self.classes)}\n".encode())
            fout.write(f"names: [{categories_str}]\n".encode())  # remove last comma

    def _write_labels_file(self, filename: str, rows : List[List]) -> None:
        file_path = pathlib.Path(self.temp_dir.name) / "labels" / f"{filename}.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as fout:
            for row in rows:
                points_str = " ".join([str(i) for i in row])
                fout.write(f"{points_str}\n".encode())


    def prepare_import(self, tasks: List[Dict]):
        raise NotImplementedError