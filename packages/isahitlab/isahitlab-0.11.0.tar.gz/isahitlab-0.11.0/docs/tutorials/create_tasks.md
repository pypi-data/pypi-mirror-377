# Task creation

You can add tasks to your batches.
It works for any kind of project.
For _Data processing_ projects, your can attach a dataset to your batch, add files on it and refer to those files when you create your tasks.

!!! info "Code Reference"
    See the [code reference](../../task/#isahitlab.actions.task.TaskActions.create_tasks) for further details.

## Usage for annotation tool projects

### Add simple task for image


```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
      "name": "folder/01.png",
      "resources": [
        "/path/to/folder/01.png"
      ]
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```

!!! info "Resources"
    Resources can be a path to a **local file** or a **public url**. The local files will be uploaded and stored by Isahit Lab.

    The `resources` field is a list of image to support "sequence" annotation. 
    If your project is not configured for image sequence annotation, it will only use the first resource.



### Add task with annotations

!!!info "Geometry formats"
    See [Geometry formats](#geometry-formats) to know more about the different formats for rectangles, polygons etc...

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
      "name": "my_task_01.png",
      "resources": [
        "/path/to/folder/01.png"
      ],
      "data": {
        "annotations": [
          {
            "polygons": [
              {
                "geometry": {
                  "vertices": [
                    0.05958132045088567,
                    0.2894211576846307,
                    0.41867954911433175,
                    0.7305389221556886
                  ],
                  "type": "rectangle"
                }
              }
            ]
          }
        ]
      }
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```

### Add task with annotations and labels


```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
      "name": "my_task_01.png",
      "resources": [
        "/path/to/folder/01.png"
      ],
      "data": {
        "annotations": [
          {
            "polygons": [
              {
                "geometry": {
                  "vertices": [
                    0.05958132045088567,
                    0.2894211576846307,
                    0.41867954911433175,
                    0.7305389221556886
                  ],
                  "type": "rectangle"
                }
              }
            ],
            "labels": {
              "my_list_id": {
                "labels": [
                  {
                    "id": "Test",
                    "name": "Test"
                  }
                ]
              }
            }
          }
        ]
      }
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```


!!! warning "Labels"
    To work properly, `my_list_id` must match a list id configured on your project


## Usage for data processing (form) projects


Data format for *Data processing* (form) project is totally function of the form configuration of the project.

!!! info "Resources"
    Tasks of *Data processing* (form) project are not resource based so you cannot simply provide the `resources` field. It will be ignored.

Let's say you have 3 inputs on your form :

| Input ID    | Type            |  Comment              |
| ----------- | --------------- | --------------------- |
| text-1      | Display text    | Image name            |
| image-1     | Resource image  | Image to be processed |
| listbox-1   | Listbox         | For ex. "Is blurry ?" |



```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
      "name": "my_task_01.png",
      "data": {
        "text-1": "Image my_task_01.png",
        "image-1": "https://my-domain.com/public/image.jpg"
      }
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```


### With resource in dataset

In the example above, we set a public url for `image-1`. In Isahit Lab, you can create a dataset and attach it to your batch.
Then you can add resources and refer to it in your tasks with `resource://folder/image.jpg`


!!! info "Code Reference"
    See the [code reference](../dataset.md) for further details.



```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

files = [
    "image1.jpg",
    {"file" : "/path/to/folder/01.png", "path": "folder"}
]

tasks_input = [
    {
      "name": "image1.jpg",
      "data": {
        "text-1": "Image image1.jpg",
        "image-1": "resource://image1.jpg"
      }
    }
    {
      "name": "01.png",
      "data": {
        "text-1": "Image folder/01.png",
        "image-1": "resource://folder/01.png"
      }
    }
]

lab.append_to_dataset(
        project_id='<project_id>',
        batch_id='<batch_id>',
        files=files)

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```

### Annotation tool in data processing (form) projects

Your form can contain annotation tools (In this example: `iat-1`).

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

files = [
    "image1.jpg",
    {"file" : "/path/to/folder/01.png", "path": "folder"}
]

tasks_input = [
    {
      "name": "image1.jpg",
      "data": {
        "text-1": "Image image1.jpg",
        "image-1": "resource://image1.jpg",
        "iat-1": {
            "resources" : ["resource://image1.jpg"]
        }
      }
    }
    {
      "name": "01.png",
      "data": {
        "text-1": "Image folder/01.png",
        "image-1": "resource://folder/01.png",
        "iat-1": {
            "resources" : ["resource://folder/01.png"],
            "annotations" : [
                ... # see "Add task with annotations" above
            ]
        }
      }
    }
]

lab.append_to_dataset(
        project_id='<project_id>',
        batch_id='<batch_id>',
        files=files)

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```


## Validation

### Unicity

The SDK will automatically raise an error if a task with the same name exists in the batch. The whole import is canceled.

To ignore duplicates and insert others tasks, set `raise_if_existing` to `False`

To skip this check and insert duplicates anyway, set `disable_unicity_check` to `True`



### Data validation

The SDK helps you to import valid data to make sure your tasks will work properly.

If you are encountering problems with validation, you can disable the validation by setting `disable_data_check` to `True`


## Geometry formats

### Rectangle annotation

```json
{
    "polygons": [
        {
        "geometry": {
            "vertices": [
            0.05958132045088567, # Top Left X relative coordinate
            0.2894211576846307,  # Top Left Y relative coordinate
            0.41867954911433175, # Bottom Right X relative coordinate
            0.7305389221556886   # Bottom Right Y relative coordinate
            ],
            "type": "rectangle"
        }
        }
    ],
    "labels": {
        "my_list_id": {
            "labels": [
                {
                "id": "Test",
                "name": "Test"
                }
            ]
        }
    }
}
```

### Polygon, graph and polyline annotation


```json
{
    "polygons": [
        {
        "geometry": {
            "vertices": [
            0.05958132045088567,  # Point X1 relative coordinate
            0.2894211576846307,   # Point Y1 relative coordinate
            0.41867954911433175,  # Point X2 relative coordinate
            0.7305389221556886,   # Point Y2 relative coordinate
            ...
            0.31867954911433175,  # Point Xn relative coordinate
            0.9305389221556886    # Point Yn relative coordinate
            ],
            "type": "polygon"
        }
        }
    ],
    "labels": {
        "my_list_id": {
            "labels": [
                {
                "id": "Test",
                "name": "Test"
                }
            ]
        }
    }
}
```


### Segmentation

!!! warning "Using helper"
    For a easier way to import segmentation data, see "Using helper" section below.

In Isahit Lab, the segmentation is "Pixel level" so the native input / output is a png mask.

To work properly, you must provide a base64 encoded mask **and** annotations list where `polygons` is a list of three number matching the RGB used in the mask. 

#### Mask

Each labeled pixel in your mask must follow this RGB convention:


| R                 | G                        |  B                                             |
| ----------------- | ------------------------ | ---------------------------------------------- |
| instance_id % 256 | floor(instance_id / 256) | Label bChannel (in your project configuration) |

newId % 256, Math.floor(newId / 256)
!!! Example
    RGB triplet : (1, 0, 7)

#### Annotations

You must aslo provide an annotation for each RGB triplet in your mask and with the label matching the B channel

```
{
    "polygons": [1, 0, 7],
    "labels": {
        "my_list_id": {
            "labels": [
                {
                    "id": "Test",
                    "name": "Test"
                }
            ]
        }
    }
}
```

#### Example 


```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
      "name": "my_task_01.png",
      "resources": [
        "/path/to/folder/01.png"
      ],
      "data": {
        "annotations": [
          {
            "polygons": [1, 0, 7]
            "labels": {
              "my_list_id": {
                "labels": [
                  {
                    "id": "Test",
                    "name": "Test"
                  }
                ]
              }
            }
          }
        ],
        "mask" : "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA (truncated)"
      }
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```


#### Using helper

You can use a helper to import segmentation task with *Rectangle* or *Polygon* data.

!!! warning "Dependencies"
    This feature requires additional dependencies. You can install then with `pip install isahitlab[image]`



```python
from isahitlab.client import IsahitLab
from isahitlab.helpers.labels import extract_labels_map_by_id
from isahitlab.helpers.segmentation import polygon_data_to_segmentation_data

lab = IsahitLab()

tasks_input = [
    {
      "name": "my_task_01.png",
      "resources": [
        "/path/to/folder/01.png"
      ],
      "data": {
        "annotations": [
          {
            "polygons": [
              {
                "geometry": {
                  "vertices": [
                    0.05958132045088567,
                    0.2894211576846307,
                    0.41867954911433175,
                    0.7305389221556886
                  ],
                  "type": "rectangle"
                }
              }
            ]
          }
        ]
      }
    }
]

# Get project configuration and extract label mapping
project_configuration = lab.project_configuration(project_id=project_id)
labels_mapping_by_id = extract_labels_map_by_id(
    project_configuration=project_configuration)

  # For each task, replace "polygon" or "rectangle" data by "segmentation" data
  tasks_input = [{
      **t,
      "data": polygon_data_to_segmentation_data(
                  t['data'], 
                  labels_mapping_by_id=labels_mapping_by_id, 
                  image_size={ 
                          "width": 800,
                          "height": 600 
                  }
      )
  } for t in tasks_input]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    tasks=tasks_input
)
```

!!! info "Image size"
    `image_size` parameter is required to build the segmentation mask.



### Kili compatibility

The SDK provide a partial compatiblity with Kili format for task creation. Set `compatibility_mode` to `kili`.

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

tasks_input = [
    {
        "name": "test4.png",
        "resources": [
            "/home/benjamin/Documents/ISAHIT SAAS/image-demo/image_2/01.png"
        ],
        "data": {
            "OBJECT_DETECTION_JOB": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {
                                        "x": 0.09589041095890412,
                                        "y": 0.2607829000381695
                                    },
                                    {
                                        "x": 0.09589041095890412,
                                        "y": 0.16281436871792687
                                    },
                                    {
                                        "x": 0.24738114423851731,
                                        "y": 0.16281436871792687
                                    },
                                    {
                                        "x": 0.24738114423851731,
                                        "y": 0.2607829000381695
                                    }
                                ],
                                "vertices": [
                                    {
                                        "x": 94.93150684931507,
                                        "y": 163.51087832393227
                                    },
                                    {
                                        "x": 94.93150684931507,
                                        "y": 102.08460918614014
                                    },
                                    {
                                        "x": 244.90733279613215,
                                        "y": 102.08460918614014
                                    },
                                    {
                                        "x": 244.90733279613215,
                                        "y": 163.51087832393227
                                    }
                                ]
                            }
                        ],
                        "categories": [
                            {
                                "name": "Test1"
                            }
                        ],
                        "children": {
                            "CLASSIFICATION_JOB": {
                                "categories": [
                                    {
                                        "confidence": 100,
                                        "name": "ENFANT_1"
                                    }
                                ]
                            },
                            "CLASSIFICATION_JOB_0": {
                                "categories": [
                                    {
                                        "children": {
                                            "TRANSCRIPTION_JOB_0": {
                                                "text": "test 2"
                                            }
                                        },
                                        "confidence": 100,
                                        "name": "ENFANT_2"
                                    },
                                    {
                                        "children": {
                                            "TRANSCRIPTION_JOB": {
                                                "text": "test"
                                            }
                                        },
                                        "confidence": 100,
                                        "name": "ENFANT_1"
                                    }
                                ]
                            }
                        },
                        "labelVersion": "default",
                        "mid": "20241128170655261-1",
                        "type": "rectangle"
                    }
                ]
            }
        }
    }
]

lab.create_tasks(
    project_id='<project_id>',
    batch_id='<batch_id>',
    compatibility_mode="kili",
    tasks=tasks_input
)
```
