from beanie import PydanticObjectId

from app.document.models import Document


class DocumentRepository:
    @staticmethod
    async def list_all(
        tenant_id: str,
        folder_path: str | None = None,
        uploaded_by: str | None = None,
    ) -> list[Document]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if folder_path:
            filt["folder_path"] = folder_path
        if uploaded_by:
            filt["uploaded_by"] = PydanticObjectId(uploaded_by)
        return await Document.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get(tenant_id: str, document_id: str) -> Document | None:
        doc = await Document.get(document_id)
        if doc and str(doc.tenant_id) == tenant_id and not doc.is_deleted:
            return doc
        return None

    @staticmethod
    async def create(tenant_id: str, data: dict) -> Document:
        doc = Document(tenant_id=PydanticObjectId(tenant_id), **data)
        await doc.insert()
        return doc

    @staticmethod
    async def update(doc: Document, data: dict) -> Document:
        for key, value in data.items():
            if value is not None:
                setattr(doc, key, value)
        await doc.touch()
        return doc

    @staticmethod
    async def soft_delete(doc: Document) -> None:
        await doc.soft_delete()
