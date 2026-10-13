
import os

from supabase import create_client


def get_storage():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "payment-proofs")

    if not url or not key:
        raise RuntimeError(
            "Configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )

    client = create_client(url, key)
    return client.storage.from_(bucket)


def upload_proof(filename: str, data: bytes, content_type: str) -> None:
    storage = get_storage()
    storage.upload(
        filename,
        data,
        file_options={
            "content-type": content_type,
            "upsert": "false",
        },
    )


def download_proof(filename: str) -> bytes:
    storage = get_storage()
    return storage.download(filename)


def delete_proof(filename: str) -> None:
    storage = get_storage()
    storage.remove([filename])
