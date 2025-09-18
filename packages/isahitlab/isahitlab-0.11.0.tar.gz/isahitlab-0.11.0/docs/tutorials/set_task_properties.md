# Task properties update

You can add set some properties on your tasks.

!!! info "Code Reference"
    See the [code reference](../../task/#isahitlab.actions.task.TaskActions.update_properties_of_tasks) for further details.

## Available properties


| Property    | Type        |
| ----------- | ----------- |
| score       | *number*    |


## Custom properties

Some properties like `score` are known by the system. 

To add custom properties, pass a dictionnary of properties in `properties.custom` (see example below).

!!! warning "Limitations"
    Only `number` and `string` are supported. Properties of type `string` are limited to 2000 characters.


## Example


```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.update_properties_of_tasks(
    project_id='<project_id>',
    task_id_in=['<task_id>'],
    properties={ 
        "score" : 5,
        "custom": {
            "my-property" : "my_value"
        }
    }
)
```


!!! neutral "Remove properties"
    Set the property to `None` to remove it