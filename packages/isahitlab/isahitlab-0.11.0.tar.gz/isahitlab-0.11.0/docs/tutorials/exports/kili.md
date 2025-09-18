# Export to Kili format

!!! info "Code Reference"
    See the [code reference](../../task.md#isahitlab.actions.task.TaskActions.export_tasks) for further details.

## Compatibility

Export to Kili format is available for:

* Project type *__Bounding Box__* (`iat-rectangle`)
* Project type *__Polygon__* (`iat-polygon`)
* Project type *__Polyline__* (`iat-polyline`)
* Project type *__Graph__* (`iat-graph`)
* Project type *__Segmentation__* (`iat-segmentation`)
* Project type *__Data processing__* (`form`) with input type:
    * *Bounding Box* (`tool-iat-rectangle`)
    * *Polygon* (`tool-iat-polygon`)
    * *Polyline* (`tool-iat-polyline`)
    * *Graph* (`tool-iat-graph`)
    * *Segmentation* (`tool-iat-segmentation`)

!!! warning "For *Data processing* project"
    The SDK will try to detect the input compatible with the export. 
    If more than one input is compatible, you must provide the `input_id` parameter to select the input to export.

## Output

JSON file

!!! info
    You can also set the `in_memory` parameter to `True` to make the `export_tasks()` function return the result as `Iterable[Dict]`

## Usage

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", format="yolo")
```

You can filter the tasks with the same parameters than you can use to [get tasks](../../task.md#isahitlab.actions.task.TaskActions.get_tasks).

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="kili", 
                 batch_id_in=["<batch_id>"], 
                 status_in=["complete", "reviewed"], 
                 updated_at_gte="2024-12-25 00:00:00"
                 )
```

Use `output_folder` and / or `output_filename` to choose where to save the results.


``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="kili", 
                 output_folder="./output",
                 output_filename="my-export.json"
                 )
```

!!! warning "Output name"
    If you set the `output_filename` parameter, it must end with `.json`

!!! info "Directory tree"
    The SDK will automatically create the folder tree if you set an `output_folder` like `output/my_outputs/<project_id>`
