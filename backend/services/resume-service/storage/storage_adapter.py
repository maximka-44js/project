import os
import uuid
from typing import Tuple

USE_S3 = os.getenv("USE_S3", "0") == "1"
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_SECURE = os.getenv("S3_SECURE", "1") == "1"
S3_PREFIX = os.getenv("S3_PREFIX", "original")

LOCAL_ROOT = os.getenv("RESUME_STORAGE_ROOT", "/data/resumes")

_s3_client = None

def _init_s3():
    global _s3_client
    if _s3_client is not None:
        return _s3_client
    if not USE_S3:
        return None
    try:
        import boto3
        _s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT or None,
            region_name=S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            use_ssl=S3_SECURE,
        )
        return _s3_client
    except ImportError:
        raise RuntimeError("boto3 not installed. Add it to requirements.txt")


def save_file(upload_file) -> Tuple[str, str]:
    """Save file either to local FS or S3 depending on USE_S3.

    Returns (stored_path_or_url, stored_key)
    """
    ext = upload_file.filename.rsplit(".", 1)[-1].lower() if "." in upload_file.filename else "bin"
    key = f"{S3_PREFIX}/{uuid.uuid4()}.{ext}"

    data = upload_file.file.read()
    upload_file.file.seek(0)

    if USE_S3:
        client = _init_s3()
        if not S3_BUCKET:
            raise RuntimeError("S3_BUCKET is not set")
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=data, ContentType=upload_file.content_type or "application/octet-stream")
        # Construct URL (may require path-style depending on provider)
        url = f"{S3_ENDPOINT.rstrip('/')}/{S3_BUCKET}/{key}" if S3_ENDPOINT else f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
        return url, key
    else:
        os.makedirs(LOCAL_ROOT, exist_ok=True)
        local_path = os.path.join(LOCAL_ROOT, key.replace("/", "_"))
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path, key
