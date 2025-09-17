# gcs_utils.py
from pyschare.chatbot.impersonation import get_storage_client
from pyschare.data_processing.config import target_service, lifetime


# Upload data to GCS
def upload_to_gcs(data, bucket_name, blob_path, content_type="application/json"):
    # Added new
    client = get_storage_client(target_service, lifetime)
    #
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(data, content_type=content_type)
    print(f"Uploaded to gs://{bucket_name}/{blob_path}")