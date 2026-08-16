import boto3
from botocore.exceptions import ClientError
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

s3 = boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    region_name="us-east-1",
)

try:
    s3.head_bucket(Bucket=settings.minio_bucket)
    print(f"Bucket already exists: {settings.minio_bucket}")

except ClientError as exc:
    error_code = exc.response.get("Error", {}).get("Code")

    if error_code in ("404", "NoSuchBucket"):
        s3.create_bucket(Bucket=settings.minio_bucket)
        print(f"Bucket created: {settings.minio_bucket}")
    else:
        raise

print("MinIO bucket validation complete.")