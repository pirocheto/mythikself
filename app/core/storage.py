from obstore.store import S3Store

from app.config import get_settings

settings = get_settings()

store = S3Store(
    config={
        "bucket": settings.S3_BUCKET_NAME,
        "endpoint": settings.S3_BUCKET_ENDPOINT,
        "access_key_id": settings.SCW_ACCESS_KEY,
        "secret_access_key": settings.SCW_SECRET_KEY,
    },
    skip_signature=False,
)
