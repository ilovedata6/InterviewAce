"""
Task status polling endpoint.

Clients use ``GET /api/v1/tasks/{task_id}`` to check the progress of
background jobs dispatched by the resume upload (or any future Celery task).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.infrastructure.tasks.celery_app import celery_app

router = APIRouter()


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED
    result: Any | None = None
    error: str | None = None


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    summary="Poll task status",
    response_description="Current status, result, or error of the background task.",
)
async def get_task_status(task_id: str):
    """
    Poll the status of a Celery background task.

    Status values:
    - **PENDING**: Task is waiting in the queue (or task ID is unknown).
    - **STARTED**: Worker has picked up the task.
    - **SUCCESS**: Task completed successfully — ``result`` contains output.
    - **FAILURE**: Task failed — ``error`` contains the exception message.
    - **RETRY**: Task failed and is being retried.
    - **REVOKED**: Task was cancelled.
    """
    result = celery_app.AsyncResult(task_id)

    response = TaskStatusResponse(
        task_id=task_id,
        status=result.status,
    )

    if result.successful():
        response.result = result.result
    elif result.failed():
        response.error = str(result.result)

    return response
