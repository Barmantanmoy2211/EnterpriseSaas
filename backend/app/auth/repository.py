import hashlib
from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.auth.models import RefreshToken, User


class AuthRepository:
    @staticmethod
    async def get_user_by_email(tenant_id: str, email: str) -> User | None:
        return await User.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "email": email.lower(),
                "is_deleted": False,
            }
        )

    @staticmethod
    async def get_user_by_email_global(email: str) -> User | None:
        return await User.find_one({"email": email.lower(), "is_deleted": False})

    @staticmethod
    async def create_user(
        tenant_id: str,
        email: str,
        password_hash: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        user = User(
            tenant_id=PydanticObjectId(tenant_id),
            email=email.lower(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )
        await user.insert()
        return user

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    async def store_refresh_token(
        tenant_id: str,
        user_id: str,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        record = RefreshToken(
            tenant_id=PydanticObjectId(tenant_id),
            user_id=PydanticObjectId(user_id),
            token_hash=AuthRepository.hash_refresh_token(token),
            expires_at=expires_at,
        )
        await record.insert()
        return record

    @staticmethod
    async def get_refresh_token(tenant_id: str, token: str) -> RefreshToken | None:
        token_hash = AuthRepository.hash_refresh_token(token)
        return await RefreshToken.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "token_hash": token_hash,
                "revoked": False,
            }
        )

    @staticmethod
    async def revoke_refresh_token(record: RefreshToken) -> None:
        record.revoked = True
        record.updated_at = datetime.now(UTC)
        await record.save()

    @staticmethod
    async def revoke_all_user_tokens(tenant_id: str, user_id: str) -> None:
        tokens = await RefreshToken.find(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "user_id": PydanticObjectId(user_id),
                "revoked": False,
            }
        ).to_list()
        for token in tokens:
            token.revoked = True
            token.updated_at = datetime.now(UTC)
            await token.save()
