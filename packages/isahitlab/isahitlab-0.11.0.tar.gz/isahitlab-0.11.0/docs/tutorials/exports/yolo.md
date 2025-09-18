# Export to Yolo format

Yolo stands for “You Only Look Once”.

[More info about the format](https://yolov8.org/yolov8-label-format)

!!! info "Code Reference"
    See the [code reference](../../task.md#isahitlab.actions.task.TaskActions.export_tasks) for further details.

## Compatibility

Export to Yolo format is available for:

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

Zip Archive

```
lab_yolo_`project_id`_`datetime`.zip/
├── data.yaml
└── labels
    ├── image_07750.jpg.txt
    ├── image_07751.jpg.txt
    └── image_07752.jpg.txt
```
**data.yaml**

```
nc: 2
names: ['label_1', 'label_2']
```

**image1.jpg.txt**

```
0 0.6545064391681276 0.4235482071561457 0.0797404071439336 0.18190535356334903
0 0.3622486209742762 0.3927660911752291 0.07606270256677716 0.15973167539023203
1 0.34460042208424047 0.5709931135225523 0.06213055937206563 0.1554331519686042
2 0.3407572947004013 0.49469991805078334 0.028823455378793328 0.03700789332585808
3 0.39520159930478876 0.5274376698390424 0.025620849225594045 0.04099335876095056
3 0.38068257272515843 0.47885714285714287 0.060650859736031015 0.09142857142857141
```


**For rectangle:** `<class> <x_center> <y_center> <width> <height>`

**For polygon:** `<class> <x> <y> <x> <y> <x> <y> ...  <x> <y>`

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
                 format="yolo", 
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
                 format="yolo", 
                 output_folder="./output",
                 output_filename="my-export.zip"
                 )
```

!!! warning "Output name"
    If you set the `output_filename` parameter, it must end with `.zip`

!!! info "Directory tree"
    The SDK will automatically create the folder tree if you set an `output_folder` like `output/my_outputs/<project_id>`