# Getting started

This is the documentation of the Python SDK for [Isahit Lab](https://lab.isahit.com).

Learn more about **isahit** [here](https://www.isahit.com).

## Installation

Install the client

```bash { .copy }
pip install isahitlab
```

## Basic usage

* Create your credentials in your lab account

!!! info Credentials
    See [isahit lab documentation](https://docs.lab.isahit.com/sdk-api-access) to know how to create your credentials

* Add the access id and the secret key to your environment variables

```bash { .copy }
export ISAHIT_LAB_API_ACCESS_ID='<your_access_id>'
export ISAHIT_LAB_API_SECRET_KEY='<your_secret_key>'
```

* Instanciate the client

```python { .copy }
from isahitlab.client import IsahitLab

lab = IsahitLab()
```


!!! info
    You can also pass your credentials as arguments during `IsahitLab` initialization:

    ```python { .copy }
    from isahitlab.client import IsahitLab

    lab = IsahitLab(
        access_id="<your_access_id>",
        secret_key="<your_secret_key>",
    )

    ```

!!! success "Try it!"
    ```python { .copy }
    lab.project_configuration(project_id=<your_project_id>)

    ```