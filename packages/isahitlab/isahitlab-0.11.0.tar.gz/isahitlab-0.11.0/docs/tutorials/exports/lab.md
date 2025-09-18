# Export to Lab format

!!! info "Code Reference"
    See the [code reference](../../task.md#isahitlab.actions.task.TaskActions.export_tasks) for further details.

## Compatibility

Export to Lab is available for all the projects.

## Output

JSON file

!!! info
    You can also set the `in_memory` parameter to `True` to make the `export_tasks()` function return the result as `Iterable[Dict]`

## Usage

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", format="lab")
```

You can filter the tasks with the same parameters than you can use to [get tasks](../../task.md#isahitlab.actions.task.TaskActions.export_tasks).

``` python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.export_tasks(project_id="<project_id>", 
                 format="lab", 
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
                 format="lab", 
                 output_folder="./output",
                 output_filename="my-export.json"
                 )
```

!!! warning "Output name"
    If you set the `output_filename` parameter, it must end with `.json`

!!! info "Directory tree"
    The SDK will automatically create the folder tree if you set an `output_folder` like `output/my_outputs/<project_id>`
