from fastapi import APIRouter, HTTPException

from ..schemas import Workspace, WorkspaceCreateRequest
from ..services.memory import memory_service

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=dict[str, list[Workspace]])
def list_workspaces():
    return {"items": memory_service.list_workspaces()}


@router.post("", response_model=Workspace, status_code=201)
def create_workspace(payload: WorkspaceCreateRequest):
    return memory_service.create_workspace(payload)


@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(workspace_id: str):
    workspace = memory_service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="WORKSPACE_NOT_FOUND")
    return workspace
