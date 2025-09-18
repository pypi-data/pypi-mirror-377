# Export segmentation masks

You can export to your disk the *pixel level* segmentation masks of your segmentation projects.

!!! warning "Dependencies"
    This export requires additional dependencies that you can install with `pip install isahitlab[image]`

!!! info "Code Reference"
    See the [code reference](../../task.md#isahitlab.actions.task.TaskActions.export_tasks) for further details.

## Compatibility

Export of masks is available for:

* Project type *__Segmentation__* (`iat-segmentation`)
* Project type *__Data processing__* (`form`) with input type:
    * *Segmentation* (`tool-iat-segmentation`)

!!! warning "For *Data processing* project"
    The SDK will try to detect the input compatible with the export. 
    If more than one input is compatible, you must provide the `input_id` parameter to select the input to export.

## Output

Folder containing .png mask

```
lab_mask_`project_id`_`datetime`/
├── image_07750.jpg.png
├── image_07751.jpg.png
└── image_07752.jpg.png
```


## Usage

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", format="mask")
```

You can filter the tasks with the same parameters than you can use to [get tasks](../../task.md#isahitlab.actions.task.TaskActions.get_tasks).

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="mask", 
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
                 format="mask", 
                 output_folder="./output",
                 output_filename="my-export"
                 )
```

!!! warning "Output name"
    If you set the `output_filename` parameter, it will be used as folder name

!!! info "Directory tree"
    The SDK will automatically create the folder tree if you set an `output_folder` like `output/my_outputs/<project_id>`


## Options

### `replace_extension`

**Type:** boolean

For each mask, the file name will be the name of the task with `.png`. If, for example, the name of your task is `my-task-01.jpg`, set this option to `True` to save your mask as `my-task-01.png` instead of `my-task-01.jpg.png`.


``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="mask", 
                 output_folder="./output",
                 output_filename="my-export",
                 options={
                    "replace_extension" : True
                 }
                )
```


### `semantic_mapping`

**Type:** Dict[str, (int,int,int)]

By defaut, each labeled pixel in your mask follows this RGB convention:


| R              | G                  |  B                                             |
| -------------- | ------------------ | ---------------------------------------------- |
| instance_id    | instance_id % 255  | Label bChannel (in your project configuration) |


You can transform you mask to get custom semantic colored mask by passing a Dict where the keys are the **label id** configured on your project and the values are the **RGB triplet** to set.


``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="mask", 
                 output_folder="./output",
                 output_filename="my-export",
                 options={
                    "semantic_mapping" : {
                        "Test 1":  (128, 64, 128),
                        "Test 2": (70, 70, 70),
                        "Test 3": (220, 220, 0)
                     }
                 }
                )
```
