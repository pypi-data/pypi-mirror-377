import json
import logging
import pathlib
from datetime import datetime
from typing import Any, Dict, List, Union

from isahitlab.helpers.data import merge_data_and_metadata
from isahitlab.helpers.labels import extract_labels_map_by_id, extract_main_labels
from isahitlab.helpers.path import check_extension

from .base import BaseFormatter

logger = logging.getLogger(__name__)

class LabToLabFormatter(BaseFormatter):
    """Formatter used to merge task data and metadata"""

    is_sequence: bool = False

    export : List[Dict[str, Any]]= None

    def __init__(self, project_configuration : Dict, options : Dict = {}) -> None :

        self._init_configuration(project_configuration, options, {
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
    
    ### Import
    def prepare_import(self, tasks):
        formatted_tasks = []
        labels = None
        ## If is IAT
        if self.is_iat_project_type():
            labels = extract_labels_map_by_id(self._project_configuration)
        for task in tasks:
            formatted_tasks.append(self._prepare_task(task, labels))
        return formatted_tasks
    
    def _prepare_task(self, task: Dict, labels : List = None) -> Dict:
        data = task.get("data", None)
        if data != None:
            prepared_data = {
                **data
            }
            ## If is IAT
            if self.is_iat_project_type():
                annotations = prepared_data.get("annotations",[])
                prepared_data["annotations"] = self._prepare_annotations(annotations, labels)
            elif self.is_form_project_type():
                iat_inputs = self.get_tool_iat_input()
                for iat_input in iat_inputs:
                    input_data = prepared_data.get(iat_input['id'], None)
                    if input_data == None:
                        continue
                    annotations = input_data.get("annotations",[])
                    input_labels_map = extract_labels_map_by_id(iat_input.get('config', {}))
                    prepared_data[iat_input['id']]["annotations"] = self._prepare_annotations(annotations, input_labels_map)
            task['data'] = prepared_data
        return task
        

    def _prepare_annotations(self, annotations: List, labels_list: Dict):
        prepared_annotations = []
        for annotation in annotations:
            labels = annotation.get("labels", {})
            main_labels = extract_main_labels(labels)
            texts = []
            colors = []
            
            for main_label in main_labels:
                label_config = labels_list.get(main_label['id'], None)
                if label_config:
                    texts.append(label_config['name'])
                    colors.append(label_config['color'])
            
            annotation_text = ", ".join(texts) if len(texts) > 0 else None
            annotation_color = colors[len(colors) - 1] if len(colors) > 0 else None

            if annotation_text and 'text' not in annotation:
                annotation['text'] = annotation_text
            if annotation_color and 'color' not in annotation:
                annotation['color'] = annotation_color
            
            prepared_annotations.append(annotation)

        return prepared_annotations

    ### Export

    def _init_export(self):
        self.export = []
    
    def append_task_to_export(self, task: Dict):
        if self.export == None:
            self._init_export()

        self.export.append(self._format_task(task))

    def complete_export(self) -> Any:
        if self.export == None:
            logger.warning('Nothing to export')
            return
        
        if self._options.get("in_memory"):
            return self.export

        now_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        default_folder = '.'
        extra_filename_part = "_{}".format(self._options.get("extra_filename_part")) if "extra_filename_part" in self._options else ""
        default_filename = f'lab{extra_filename_part}_{now_str}.json'
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
            **task,
            "data" : self._map_data_body(task)
        }

        return formatted_task


    def _map_data_body(self, task: Dict) -> Union[Dict, None]:
        if not task.get("data",None):
            return {}        
        
        data = task["data"].get("body", None)
        metadata = (task["data"].get("metadata", {}) or {}).get("body", None)
        if not data and not metadata:
            return None
        
        merged_data = merge_data_and_metadata(data, metadata)

        return merged_data
        
