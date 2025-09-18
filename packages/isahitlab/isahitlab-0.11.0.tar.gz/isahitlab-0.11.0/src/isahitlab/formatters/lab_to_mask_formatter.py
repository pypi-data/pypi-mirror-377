import base64
import logging
import pathlib
from datetime import datetime
from typing import Dict, List, Tuple

from isahitlab.helpers.labels import extract_labels_map_by_id

from .base import BaseFormatter

try:
    import cv2  # type: ignore
    import numpy as np
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
        "OpenCV and Numpy are required to use the mask export. To install them,"
        " run: pip install isahitlab[image]."
    ) from err


logger = logging.getLogger(__name__)

class LabToMaskFormatter(BaseFormatter):
    """Formatter to export segmentation masks 
    
    **Output folder**

    - output/
        - image1.jpg.png
        - image2.png
    

    """

    output_folder: str = None
    replace_extension: bool = False
    b_channel_mapping: Dict[int,Tuple[int,int,int]] = None

    def __init__(self, project_configuration : Dict, options : Dict = {}) -> None :
        
        if options.get("in_memory", None):
            raise Exception('"in_memory" not supported')
        
        self._init_configuration(project_configuration, options, {
            "compatible_types" : [
                "form.tool-iat-segmentation", 
                "iat-segmentation"
            ]
        })

        # Check if is sequence
        if self._project_configuration.get("metadata", {}).get("toolOptions", {}).get("sequence", False):
            raise Exception('LabToMaskFormatter does not support sequences')
        
        self.replace_extension = self._options.get('replace_extension' , False)

        if self._options.get("semantic_mapping", None):
            self.b_channel_mapping = extract_labels_map_by_id(self._project_configuration, field="bChannel") 
    
    ### Transform

    def format_tasks(self, tasks: List[Dict]) -> List[Dict]:
        formatted_tasks = []

        for task in tasks:
            formatted_task = self._format_task(task)
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    
    ### Export

    def _init_export(self):
        now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        default_folder = '.'
        extra_filename_part = "_{}".format(self._options.get("extra_filename_part")) if "extra_filename_part" in self._options else ""
        default_filename = f'lab_mask{extra_filename_part}_{now_str}'
        output_folder = self._options.get("output_folder", None) or default_folder
        outputfile_path = "{}/{}".format(output_folder, self._options.get("output_filename", None) or default_filename)

        self.output_folder = outputfile_path
        path_folder = pathlib.Path(self.output_folder)
        path_folder.mkdir(parents=True, exist_ok=False)

    def append_task_to_export(self, task: Dict):
        if self.output_folder == None:
            self._init_export()

        mask = self._format_task(task)
        task_name = task["name"]
        if mask:
            self._write_mask(task_name, mask)

    def complete_export(self):
        if self.output_folder == None:
            logger.warning('Nothing to export')
            return
                
        print("Exported to \"{}\"".format(str(pathlib.Path(self.output_folder).absolute())))

    def _format_task(self, task : Dict) -> Dict:
        task = self._normalize_task(task)
        mask = task.get("data", {}).get("body", {}).get("mask", None)
        return mask

    def _write_mask(self, task_name: str, mask : str) -> None:
        if self.replace_extension and task_name.rfind('.') > -1:
            task_name = task_name[0:task_name.rfind('.')]

        file_path = pathlib.Path(self.output_folder) / f"{task_name}.png"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        img = self._data_uri_to_cv2_img(mask)

        if self._options.get("semantic_mapping", None):
            img = self._transform_mask(img)

        cv2.imwrite(str(file_path), img)
    
    def _transform_mask(self, img):
        semantic_mapping = self._options.get("semantic_mapping", None)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        for m in semantic_mapping:
            b_channel = self.b_channel_mapping.get(m, None)
            if not b_channel:
                continue
            lower = np.array([1, 0, b_channel])
            upper = np.array([255, 255, b_channel])
            to = semantic_mapping[m]
            mask = cv2.inRange(imgRGB, lower, upper)
            imgRGB[mask>0] = to
        
        imgBGR = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)

        return imgBGR

    def _data_uri_to_cv2_img(self, uri):
        encoded_data = uri.split(',')[1]
        decoded_data = base64.b64decode(encoded_data)
        nparr = np.fromstring(decoded_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    

    def prepare_import(self, tasks: List[Dict]):
        raise NotImplementedError