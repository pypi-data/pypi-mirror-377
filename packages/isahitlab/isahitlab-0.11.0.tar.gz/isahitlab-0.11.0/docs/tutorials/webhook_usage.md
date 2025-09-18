# Webhook usage

You can setup a webhook on your batches.

!!! info "Code Reference"
    See the [code reference](../webhook.md) for further details.

A webhook is **attached to a batch**, but you can easily define a webhook for all the batches in a project.

!!! warning "New batch"
    If you create a new batch, you have to set the webhook on it. If you use the same webhook parameters for all the batches of your project,
    you can call `setup_webhook` with only a `project_id` parameter. It will update the webhook of all the batches on your projects without loosing
    the "log" information (`lastCall` and `lastError`)

## Usage

Setup a simple webhook on all batches on my project

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.setup_webhook(
    project_id='<project_id>',
    webhook_url='<my_url>'
)
```

!!! warning "URL"
    The `webhook_url` must start with `http`

You can also setup a webhook for a specific batch

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.setup_webhook(
    project_id='<project_id>',
    batch_id='<batch_id>',
    webhook_url='<my_url>'
)
```

To check the webhook of a batch, you can use `get_webhook`

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

my_webhook = lab.get_webhook(
    project_id='<project_id>',
    batch_id='<batch_id>'
)

json.dumps(my_webhook, indent=2)

```

## Log

You can only know the information of the last call (`lastCall`). 

Isahit Lab also keep the last error (`lastError`).
The body of the response is stored to facilitate debugging.

See the code below and the output.

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

my_webhook = lab.get_webhook(
    project_id='<project_id>',
    batch_id='<batch_id>'
)

json.dumps(my_webhook, indent=2)

```

Output:

```json
{
  "header": "<my_authorization_token>",
  "url": "<my_url>",
  "updatedAt": "2024-12-17T15:23:21.433Z",
  "lastCall": {
    "statusCode": 200,
    "message": "OK",
    "date": "2024-12-17T15:10:37.619Z"
  },
  "lastError": {
    "statusCode": 400,
    "message": "Bad Request",
    "body": {
        ...
    }
  }
}
```

## Authorization

You can define a **header** that will be sent as the _Authorization_ header of the request.

```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.setup_webhook(
    project_id='<project_id>',
    webhook_url='<my_url>',
    webhook_header='<my_authorization_token>'
)
```

## Request

Isahit Lab will make a **POST** call on your URL.

```json
{
    "workflowId": string,
    "type": "annotation" | "review",
    "taskId": string,
    "batchId": string,
    "projectId": string
}
```

!!! info "type"
    `type` lets you know if the task has been done in an **annotation** job or a **review** job

You can now use the SDK to get your task.
