# SPDX-FileCopyrightText: 2024-present Benjamin Piogé <benjamin@isahit.com>
#
# SPDX-License-Identifier: MIT
from typing import Dict

from isahitlab.domain.export import ExportFormat
from isahitlab.domain.task import TaskCompatibilityMode

from .base import BaseFormatter
from .kili_to_lab_formatter import KiliToLabFormatter
from .lab_to_kili_formatter import LabToKiliFormatter
from .lab_to_lab_formatter import LabToLabFormatter
from .lab_to_yolo_formatter import LabToYoloFormatter
try:
    from .lab_to_mask_formatter import LabToMaskFormatter
except:
    pass


def get_compatibility_formatter(from_mode : TaskCompatibilityMode, to_mode : TaskCompatibilityMode, project_configuration : Dict) -> BaseFormatter :
    """Factory"""
    if from_mode == "lab" and to_mode == "kili":
        return LabToKiliFormatter(project_configuration)
    if from_mode == "kili" and to_mode == "lab":
        return KiliToLabFormatter(project_configuration)
    if from_mode == "lab" and to_mode == "lab":
        return LabToLabFormatter(project_configuration)

def get_creation_formatter(from_mode : TaskCompatibilityMode, project_configuration : Dict) -> BaseFormatter :
    """Factory"""
    if from_mode == "lab":
        return LabToLabFormatter(project_configuration)
    
def get_export_formatter(from_format : ExportFormat, to_format : ExportFormat, project_configuration : Dict, options: Dict = {}) -> BaseFormatter :
    """Factory"""
    if from_format == "lab" and to_format == "kili":
        return LabToKiliFormatter(project_configuration, options)
    if from_format == "lab" and to_format == "yolo":
        return LabToYoloFormatter(project_configuration, options)
    if from_format == "lab" and to_format == "lab":
        return LabToLabFormatter(project_configuration, options)
    if from_format == "lab" and to_format == "mask":
        try:
            return LabToMaskFormatter(project_configuration, options)
        except:
            raise ModuleNotFoundError(
                "OpenCV and Numpy are required to use the mask export. To install them,"
                " run: pip install isahitlab[image]."
            )
    
