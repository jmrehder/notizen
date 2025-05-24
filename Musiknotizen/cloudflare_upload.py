def upload_to_r2(file_bytes, key, content_type, account_id, access_key, secret_key, bucket):
    import requests
    from requests.auth import HTTPBasicAuth

    # R2 Storage API (S3-kompatibel)
    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    url = f"{endpoint}/{bucket}/{key}"

    headers = {
        "Content-Type": content_type,
    }
    # S3-Signature v4 Auth/Session muss ggf. korrekt eingebaut werden – Beispiel geht von Public Bucket aus!
    response = requests.put(
        url,
        data=file_bytes,
        headers=headers,
        auth=HTTPBasicAuth(access_key, secret_key),
    )
    if response.status_code not in (200, 201):
        raise Exception(f"Upload fehlgeschlagen: {response.text}")

    # **Erzeuge Public Development URL**
    PUBLIC_BASE = "https://pub-c56498495f1a46e08d1d447f1418bbb7.r2.dev"
    public_url = f"{PUBLIC_BASE}/{key}"
    return public_url
