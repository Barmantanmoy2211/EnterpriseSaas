from fastapi import APIRouter, Depends, Query, status

from app.document.schemas import DocumentCreate, DocumentResponse, DocumentUpdate
from app.document.service import DocumentService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    folder_path: str | None = Query(None),
    uploaded_by: str | None = Query(None),
    user=Depends(require_permission("document", "read")),
):
    return await DocumentService.list_documents(str(user.tenant_id), folder_path, uploaded_by)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, user=Depends(require_permission("document", "read"))):
    return await DocumentService.get_document(str(user.tenant_id), document_id)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    user=Depends(require_permission("document", "manage")),
):
    return await DocumentService.create_document(str(user.tenant_id), data, str(user.id))


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    user=Depends(require_permission("document", "manage")),
):
    return await DocumentService.update_document(str(user.tenant_id), document_id, data, str(user.id))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user=Depends(require_permission("document", "manage")),
):
    await DocumentService.delete_document(str(user.tenant_id), document_id, str(user.id))
