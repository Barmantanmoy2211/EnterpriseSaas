from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.document.models import Document
from app.document.repository import DocumentRepository
from app.document.schemas import DocumentCreate, DocumentResponse, DocumentUpdate
from app.search.repository import SearchRepository
from app.shared.exceptions import NotFoundError


class DocumentService:
    @staticmethod
    def _response(doc: Document) -> DocumentResponse:
        return DocumentResponse(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
            file_url=doc.file_url,
            mime_type=doc.mime_type,
            size_bytes=doc.size_bytes,
            folder_path=doc.folder_path,
            uploaded_by=str(doc.uploaded_by),
            tags=doc.tags,
            related_entity_type=doc.related_entity_type,
            related_entity_id=doc.related_entity_id,
            version=doc.version,
            metadata=doc.metadata,
        )

    @staticmethod
    async def _index(doc: Document) -> None:
        await SearchRepository.upsert(
            str(doc.tenant_id),
            "document",
            str(doc.id),
            doc.title,
            doc.description,
            doc.tags + [doc.folder_path],
            {"mime_type": doc.mime_type},
        )

    @staticmethod
    async def list_documents(
        tenant_id: str,
        folder_path: str | None = None,
        uploaded_by: str | None = None,
    ) -> list[DocumentResponse]:
        docs = await DocumentRepository.list_all(tenant_id, folder_path, uploaded_by)
        return [DocumentService._response(d) for d in docs]

    @staticmethod
    async def get_document(tenant_id: str, document_id: str) -> DocumentResponse:
        doc = await DocumentRepository.get(tenant_id, document_id)
        if doc is None:
            raise NotFoundError("Document not found")
        return DocumentService._response(doc)

    @staticmethod
    async def create_document(tenant_id: str, data: DocumentCreate, actor_id: str) -> DocumentResponse:
        payload = data.model_dump()
        payload["uploaded_by"] = PydanticObjectId(actor_id)

        doc = await DocumentRepository.create(tenant_id, payload)
        await DocumentService._index(doc)
        await AuditService.log_event(tenant_id, "document.created", "document", str(doc.id), actor_id)
        return DocumentService._response(doc)

    @staticmethod
    async def update_document(
        tenant_id: str, document_id: str, data: DocumentUpdate, actor_id: str
    ) -> DocumentResponse:
        doc = await DocumentRepository.get(tenant_id, document_id)
        if doc is None:
            raise NotFoundError("Document not found")

        updates = data.model_dump(exclude_unset=True)
        if data.file_url is not None and data.file_url != doc.file_url:
            updates["version"] = doc.version + 1

        doc = await DocumentRepository.update(doc, updates)
        await DocumentService._index(doc)
        await AuditService.log_event(tenant_id, "document.updated", "document", str(doc.id), actor_id)
        return DocumentService._response(doc)

    @staticmethod
    async def delete_document(tenant_id: str, document_id: str, actor_id: str) -> None:
        doc = await DocumentRepository.get(tenant_id, document_id)
        if doc is None:
            raise NotFoundError("Document not found")
        await DocumentRepository.soft_delete(doc)
        await AuditService.log_event(tenant_id, "document.deleted", "document", str(doc.id), actor_id)
