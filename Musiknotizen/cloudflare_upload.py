import boto3
from botocore.client import Config

def get_r2_client(account_id, access_key, secret_key):
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    session = boto3.session.Session()
    return session.client(
        service_name='s3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        config=Config(signature_version="s3v4"),
        region_name="auto"
    )

def upload_to_r2(file_bytes, filename, content_type, cf_account_id, cf_access_key, cf_secret_key, cf_bucket):
    client = get_r2_client(cf_account_id, cf_access_key, cf_secret_key)
    client.put_object(
        Bucket=cf_bucket,
        Key=filename,
        Body=file_bytes,
        ContentType=content_type,
        ACL='public-read'
    )
    # Return public URL
    return f"https://{cf_account_id}.r2.cloudflarestorage.com/{cf_bucket}/{filename}"
