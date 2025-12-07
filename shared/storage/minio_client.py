# shared/storage/minio_client.py
import io
from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from shared.core.config import settings


def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure,
    )



def ensure_bucket_exists(bucket_name: str | None = None) -> None:
    """
    Гарантирует, что бакет существует: если нет - создаёт.
    Если bucket_name не указан, берётся бакет для резюме.
    """
    client = get_minio_client()
    bucket = bucket_name or settings.minio.resumes_bucket

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_resume_object(object_name: str, data: bytes, content_type: str | None = None) -> None:
    client = get_minio_client()
    bucket = settings.minio.resumes_bucket

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    file_like = io.BytesIO(data)
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=file_like,
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )


def generate_presigned_url(
    object_name: str,
    expires: timedelta = timedelta(minutes=10),
) -> str:
    """
    Генерирует временную ссылку на скачивание файла резюме.
    """
    client = get_minio_client()
    return client.presigned_get_object(
        bucket_name=settings.minio.resumes_bucket,
        object_name=object_name,
        expires=expires,
    )
