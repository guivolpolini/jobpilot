import os
from abc import ABC, abstractmethod
from typing import BinaryIO
import boto3
from botocore.client import Config
from app.core.config import settings


class BaseStorageService(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, filename: str) -> str:
        """Salva arquivo e retorna o caminho ou URL acessível"""
        pass


class LocalStorageService(BaseStorageService):
    def __init__(self, upload_dir: str = settings.STORAGE_LOCAL_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_content: bytes, filename: str) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file_content)
        return f"/uploads/{filename}"


class S3StorageService(BaseStorageService):
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4")
        )
        self.bucket = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
            except Exception:
                pass

    def upload_file(self, file_content: bytes, filename: str) -> str:
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=file_content,
            ContentType="application/pdf"
        )
        return f"{settings.S3_ENDPOINT_URL}/{self.bucket}/{filename}"


def get_storage_service() -> BaseStorageService:
    if settings.STORAGE_TYPE.lower() == "s3":
        return S3StorageService()
    return LocalStorageService()
