# (C) Copyright 2024- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""Job Monitoring API Router."""

import asyncio
import io
import json
import logging
import os
import pathlib
import zipfile
from dataclasses import dataclass
from typing import Literal

import cascade.gateway.api as api
import cascade.gateway.client as client
import orjson
from cascade.controller.report import JobId
from cascade.low.core import DatasetId, TaskId
from fastapi import APIRouter, Body, Depends, HTTPException, Response, UploadFile
from fastapi.responses import HTMLResponse
from forecastbox.api.execution import SubmitJobResponse, execute
from forecastbox.api.routers.gateway import Globals
from forecastbox.api.types import ExecutionSpecification, VisualisationOptions
from forecastbox.api.utils import encode_result
from forecastbox.api.visualisation import visualise
from forecastbox.auth.users import current_active_user
from forecastbox.config import config
from forecastbox.db.job import delete_all, delete_one, get_all, get_one, update_one
from forecastbox.schemas.job import JobRecord
from forecastbox.schemas.user import UserRead

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["job"],
    responses={404: {"description": "Not found"}},
)


STATUS = Literal["submitted", "running", "completed", "errored", "invalid", "timeout", "unknown"]


@dataclass
class JobProgressResponse:
    """Job Progress Response."""

    progress: str
    """Progress of the job as a percentage."""
    status: STATUS
    """Status of the job."""
    created_at: str | None = None
    """Creation timestamp of the job."""
    error: str | None = None
    """Error message if the job encountered an error, otherwise None."""

def build_response(record: JobRecord, progress: str|None=None, error: str|None=None, status: STATUS|None=None) -> JobProgressResponse:
    created_at = str(record.created_at)
    progress = progress or record.progress or "0.00"
    error = error or record.error
    status = status or record.status
    return JobProgressResponse(progress=progress, created_at=created_at, status=status, error=error)

@dataclass
class JobProgressResponses:
    """Job Progress Responses.

    Contains progress information for multiple jobs.
    """

    progresses: dict[JobId, JobProgressResponse]
    """A dictionary mapping job IDs to their progress responses."""
    error: str | None = None
    """An error message if there was an issue retrieving job progress, otherwise None."""


def validate_job_id(job_id: JobId) -> JobId | None:
    """Validate the job ID."""
    # NOTE we could query the db here, but since next step is a conditional db retrieval anyway, this extra query makes low sense
    return job_id


def validate_dataset_id(dataset_id: str) -> str:
    """Validate the dataset ID."""
    return dataset_id


async def update_and_get_progress(job_id: JobId) -> JobProgressResponse:
    """Updates the job db with the newest cascade gateway response, returns the updated result"""
    job = await get_one(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")

    if job.status in ("running", "submitted"):
        try:
            response: api.JobProgressResponse = client.request_response(
                api.JobProgressRequest(job_ids=[job_id]), f"{config.cascade.cascade_url}"
            )  # type: ignore
        except TimeoutError:
            # NOTE we dont update db because the job may still be running
            return build_response(job, status="timeout", error="failed to communicate with gateway")
        except Exception as e:
            logger.debug(f"inquiry for {job_id=} failed with {repr(e)}")
            # TODO this is either network or internal (eg serde) problem. Ideally fine-grain network into TimeoutError branch
            result = {"status": "unknown", "error": f"internal cascade failure: {repr(e)}"}
            await update_one(job_id, **result)
            return build_response(job, **result)
        if response.error:
            # NOTE we dont update db because the job may still be running
            return build_response(job, status="unknown", error=response.error)

        jobprogress = response.progresses.get(job_id)
        if jobprogress is None:
            result = {"status": "invalid", "error": "evicted from gateway"}
            await update_one(job_id, **result)
            return build_response(job, **result)
        elif jobprogress.failure:
            result = {"status": "errored", "error": jobprogress.failure}
            await update_one(job_id, **result)
            return build_response(job, **result)
        elif jobprogress.completed or jobprogress.pct == "100.00":
            result = {"status": "completed", "progress": "100.00"}
            await update_one(job_id, **result)
            return build_response(job, **result)
        else:
            result = {"status": "running", "progress": jobprogress.pct}
            await update_one(job_id, **result)
            return build_response(job, **result)

    else:
        return build_response(job)


@router.get("/status")
async def get_status() -> JobProgressResponses:
    """Get progress of all tasks recorded in the database."""

    job_records = await get_all()

    progresses = {
        job.job_id: (
            await update_and_get_progress(job.job_id)
            if job.status in ["running", "submitted"]
            else JobProgressResponse(
                progress="0.00" if not job.status == "completed" else "100.00",
                status=job.status,
                created_at=str(job.created_at),
                error=job.error,
            )
        )
        for job in job_records
    }

    return JobProgressResponses(progresses=progresses, error=None)


@router.get("/{job_id}/status")
async def get_status_of_job(job_id: JobId = Depends(validate_job_id)) -> JobProgressResponse:
    """Get progress of a particular job."""
    return await update_and_get_progress(job_id)


@router.get("/{job_id}/outputs")
async def get_outputs_of_job(job_id: JobId = Depends(validate_job_id)) -> list[TaskId]:
    """Get outputs of a job."""
    job = await get_one(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")
    return json.loads(job.outputs)


@router.post("/{job_id}/visualise")
async def visualise_job(
    job_id: JobId = Depends(validate_job_id), options: VisualisationOptions = Body(None)
) -> HTMLResponse:
    """Visualise a job's execution graph.

    Retrieves the job's graph specification from the database, converts it to a cascade graph,
    and generates an HTML visualisation of the graph.
    """
    job = await get_one(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")
    if not options:
        options = VisualisationOptions()
    if job.graph_specification is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} had no specification.")
    spec = ExecutionSpecification(**json.loads(job.graph_specification))
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, visualise, spec, options)  # CPU bound


@router.get("/{job_id}/specification")
async def get_job_specification(job_id: JobId = Depends(validate_job_id)) -> ExecutionSpecification:
    """Get specification in the database of a job."""
    job = await get_one(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")
    if job.graph_specification is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} had no specification.")
    return ExecutionSpecification(**json.loads(job.graph_specification))


@router.get("/{job_id}/restart")
async def restart_job(
    job_id: JobId = Depends(validate_job_id), user: UserRead | None = Depends(current_active_user)
) -> SubmitJobResponse:
    """Restart a job by executing its specification."""
    job = await get_one(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")
    spec = job.graph_specification
    if not spec:
        raise HTTPException(status_code=404, detail=f"Job {job_id} had no specification.")
    spec = ExecutionSpecification(**json.loads(spec))
    return await execute(spec, user)


@router.post("/upload")
async def upload_job(file: UploadFile, user: UserRead | None = Depends(current_active_user)) -> SubmitJobResponse:
    """Upload a job specification file and execute it."""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided for upload.")
    spec = await file.read()
    spec = ExecutionSpecification(**json.loads(spec))
    return await execute(spec, user=user)


@dataclass
class DatasetAvailabilityResponse:
    """Dataset Availability Response."""

    available: bool
    """Indicates whether the dataset is available for download."""


@router.get("/{job_id}/available")
async def get_job_availablity(job_id: JobId = Depends(validate_job_id)) -> list[TaskId]:
    """Check which results are available for a given job_id.

    Parameters
    ----------
    job_id : str
        Job ID of the task

    Returns
    -------
    list[TaskId]
        List of dataset IDs that are available for the job.
    """
    response: api.JobProgressResponse = client.request_response(
        api.JobProgressRequest(job_ids=[job_id]), f"{config.cascade.cascade_url}"
    )
    return [x.task for x in response.datasets[job_id]]


@router.get("/{job_id}/{dataset_id}/available")
async def get_result_availablity(
    job_id: JobId = Depends(validate_job_id), dataset_id: TaskId = Depends(validate_dataset_id)
) -> DatasetAvailabilityResponse:
    """Check if the result is available for a given job_id and dataset_id.

    This is used to check if the result is available for download.

    Parameters
    ----------
    job_id : str
        Job ID of the task
    dataset_id : str
        Dataset ID of the task

    Returns
    -------
    DatasetAvailabilityResponse
        {'available': Availability of the result}
    """

    try:
        response: api.JobProgressResponse = client.request_response(
            api.JobProgressRequest(job_ids=[job_id]), f"{config.cascade.cascade_url}"
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Job retrieval failed: {e}")

    if job_id not in response.datasets:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found in the database.")

    return DatasetAvailabilityResponse(dataset_id in [x.task for x in response.datasets[job_id]])


@router.get("/{job_id}/logs")
async def get_logs(job_id: JobId = Depends(validate_job_id)) -> Response:
    """Returns a zip file with logs and other data for the purpose of troubleshooting"""

    logger.debug(f"getting logs for {job_id}")
    try:
        db_entity_raw = await get_one(job_id)
        db_entity = {c.name: getattr(db_entity_raw, c.name) for c in db_entity_raw.__table__.columns}
    except Exception as e:
        db_entity = {"error": repr(e)}
    logger.debug(f"{db_entity=} for {job_id}")

    try:
        request = api.JobProgressRequest(job_ids=[job_id])
        gw_state = client.request_response(request, f"{config.cascade.cascade_url}").model_dump()
    except TimeoutError:
        gw_state = {"progresses": {}, "datasets": {}, "error": "TimeoutError"}
    except Exception as e:
        gw_state = {"progresses": {}, "datasets": {}, "error": repr(e)}
    logger.debug(f"{gw_state=} for {job_id}")

    def _build_zip() -> tuple[bytes, str]:
        try:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("db_entity.json", orjson.dumps(db_entity))
                zf.writestr("gw_state.json", orjson.dumps(gw_state))
                if not Globals.logs_directory:
                    zf.writestr("logs_directory.error.txt", "logs directory missing")
                else:
                    p = pathlib.Path(Globals.logs_directory.name)
                    f = ""
                    try:
                        for f in os.listdir(p):
                            jPref = f"job.{job_id}"
                            if f.startswith("gateway") or f.startswith(jPref):
                                zf.write(f"{p/f}", arcname=f)
                    except Exception as e:
                        zf.writestr("logs_directory.error.txt", f"{f} => {repr(e)}")
            return buffer.getvalue(), ""
        except Exception as e:
            logger.exception("building zip")
            return b"", repr(e)

    loop = asyncio.get_running_loop()
    bytez, error = await loop.run_in_executor(None, _build_zip)  # IO bound

    if not error:
        return Response(
            content=bytez,
            status_code=200,
            media_type="application/zip",
        )
    else:
        return Response(
            content=error,
            status_code=500,
            media_type="text/plain",
        )


# TODO refactor this endpoint to /job_id/results/dataset_id, otherwise consumes too much
# eg /job_id/available or /job_id/logs become order-dependent / conflicting with output of such name
@router.get("/{job_id}/{dataset_id}")
async def get_result(
    job_id: JobId = Depends(validate_job_id), dataset_id: TaskId = Depends(validate_dataset_id)
) -> Response:
    """Get the result of a job.

    Parameters
    ----------
    job_id : JobId
        Job ID of the task, expected to be the id in the database, not the cascade job id.
    dataset_id : TaskId
        Dataset ID of the task, these can be found from /{job_id}/outputs.

    Returns
    -------
    Response
        Response containing the result of the job, encoded as bytes.

    Raises
    ------
    HTTPException
        If the result retrieval fails or if the job or dataset ID is not found in the database.
    """
    response = client.request_response(
        api.ResultRetrievalRequest(job_id=job_id, dataset_id=DatasetId(task=dataset_id, output="0")),
        f"{config.cascade.cascade_url}",
    )

    if response.error:
        raise HTTPException(500, f"Result retrieval failed: {response.error}")

    try:
        bytez, media_type = encode_result(response)
    except Exception as e:
        logger.exception("decoding failure")
        raise HTTPException(500, f"Result decoding failed: {repr(e)}")

    return Response(bytez, media_type=media_type)


@dataclass
class JobDeletionResponse:
    """Job Deletion Response."""

    deleted_count: int
    """Number of jobs deleted from the database."""


@router.post("/flush")
async def flush_job() -> JobDeletionResponse:
    """Flush all job from the database and cascade.

    Returns number of deleted jobs.
    """
    try:
        client.request_response(api.ResultDeletionRequest(datasets={}), f"{config.cascade.cascade_url}")  # type: ignore
    except Exception as e:
        raise HTTPException(500, f"Job deletion failed: {e}")
    finally:
        deleted_count = await delete_all()
    return JobDeletionResponse(deleted_count=deleted_count)


@router.delete("/{job_id}")
async def delete_job(job_id: JobId = Depends(validate_job_id)) -> JobDeletionResponse:
    """Delete a job from the database and cascade.

    Returns number of deleted jobs.
    """
    try:
        client.request_response(api.ResultDeletionRequest(datasets={job_id: []}), f"{config.cascade.cascade_url}")  # type: ignore
    except Exception as e:
        raise HTTPException(500, f"Job deletion failed: {e}")
    finally:
        deleted_count = await delete_one(job_id)
    return JobDeletionResponse(deleted_count=deleted_count)
