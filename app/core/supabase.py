"""Supabase client and utilities for storage and real-time features."""

import os
from typing import Optional

from supabase import create_client, Client
from app.core.config import settings


class SupabaseManager:
    """Supabase client manager for storage and auth."""

    _client: Optional[Client] = None
    _service_client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Optional[Client]:
        """Get Supabase client (anon key for client-side operations)."""
        if cls._client is None and settings.is_supabase_configured:
            cls._client = create_client(settings.supabase_url, settings.supabase_key)
        return cls._client

    @classmethod
    def get_service_client(cls) -> Optional[Client]:
        """Get Supabase service client (service key for server-side operations)."""
        if cls._service_client is None and settings.supabase_service_key:
            cls._service_client = create_client(
                settings.supabase_url, settings.supabase_service_key
            )
        return cls._service_client

    @classmethod
    def upload_file(
        cls,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
    ) -> Optional[dict]:
        """
        Upload file to Supabase Storage.

        Args:
            bucket: Storage bucket name
            path: File path in bucket
            file_data: File bytes
            content_type: MIME type

        Returns:
            Upload response or None if failed
        """
        client = cls.get_service_client()
        if not client:
            return None

        try:
            result = client.storage.from_(bucket).upload(
                path=path,
                file=file_data,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            return result
        except Exception as e:
            print(f"Supabase upload error: {e}")
            return None

    @classmethod
    def get_public_url(cls, bucket: str, path: str) -> Optional[str]:
        """Get public URL for a file in Supabase Storage."""
        client = cls.get_client()
        if not client:
            return None

        try:
            result = client.storage.from_(bucket).get_public_url(path)
            return result
        except Exception as e:
            print(f"Supabase get_public_url error: {e}")
            return None

    @classmethod
    def delete_file(cls, bucket: str, paths: list[str]) -> bool:
        """Delete files from Supabase Storage."""
        client = cls.get_service_client()
        if not client:
            return False

        try:
            client.storage.from_(bucket).remove(paths)
            return True
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False

    @classmethod
    def list_files(cls, bucket: str, folder: str = "") -> list:
        """List files in Supabase Storage bucket."""
        client = cls.get_client()
        if not client:
            return []

        try:
            return client.storage.from_(bucket).list(folder)
        except Exception as e:
            print(f"Supabase list error: {e}")
            return []


# Convenience functions
async def upload_complaint_photo(complaint_id: str, file_data: bytes, content_type: str) -> Optional[str]:
    """
    Upload complaint photo to Supabase Storage.

    Args:
        complaint_id: Complaint UUID
        file_data: Image bytes
        content_type: Image MIME type

    Returns:
        Public URL or None if failed
    """
    path = f"complaints/{complaint_id}/photo.jpg"
    result = SupabaseManager.upload_file(
        bucket=settings.storage_bucket,
        path=path,
        file_data=file_data,
        content_type=content_type,
    )

    if result:
        return SupabaseManager.get_public_url(settings.storage_bucket, path)
    return None


async def upload_facility_image(facility_id: str, file_data: bytes, content_type: str) -> Optional[str]:
    """
    Upload facility image to Supabase Storage.

    Args:
        facility_id: Facility UUID
        file_data: Image bytes
        content_type: Image MIME type

    Returns:
        Public URL or None if failed
    """
    path = f"facilities/{facility_id}/image.jpg"
    result = SupabaseManager.upload_file(
        bucket=settings.storage_bucket,
        path=path,
        file_data=file_data,
        content_type=content_type,
    )

    if result:
        return SupabaseManager.get_public_url(settings.storage_bucket, path)
    return None