import io

import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    region_name="us-east-1",
)


def upload_bytes(data: bytes, object_name: str) -> None:
    """Upload bytes to the project object-storage bucket."""
    s3_client.upload_fileobj(
        io.BytesIO(data),
        settings.minio_bucket,
        object_name,
    )


def download_bytes(object_name: str) -> bytes:
    """Download an object and return its contents as bytes."""
    buffer = io.BytesIO()
    s3_client.download_fileobj(
        settings.minio_bucket,
        object_name,
        buffer,
    )
    return buffer.getvalue()


def list_objects(prefix: str = "") -> list[str]:
    """List object names under an optional prefix."""
    response = s3_client.list_objects_v2(
        Bucket=settings.minio_bucket,
        Prefix=prefix,
    )

    return [
        item["Key"]
        for item in response.get("Contents", [])
    ]


def delete_object(object_name: str) -> None:
    """Delete an object from the project bucket."""
    s3_client.delete_object(
        Bucket=settings.minio_bucket,
        Key=object_name,
    )