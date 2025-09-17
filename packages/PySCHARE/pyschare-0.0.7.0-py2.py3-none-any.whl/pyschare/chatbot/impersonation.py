# impersonation.py

# Different Approach for impersonation
from google.auth import default
from google.auth.impersonated_credentials import Credentials as ImpersonatedCredentials
from google.cloud import storage
import vertexai

# 1. Impersonated credentials

def get_impersonation(target_service:str, lifetime:int):
    """
    Returns impersonated credentials using the default credentials as source.
    """
    # 1. Base credentials
    source_credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return ImpersonatedCredentials(
        source_credentials=source_credentials,
        target_principal=target_service,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        lifetime=lifetime
    )

def get_storage_client(target_service:str, lifetime:int):
    """
    Returns a GCS client using impersonated credentials.
    """
    c = get_impersonation(target_service, lifetime)
    return storage.Client(credentials=c)

def get_vertex(target_service:str,lifetime:int, project:str, location:str):
    """
    Initializes the Vertex AI SDK using impersonated credentials.
    """
    c = get_impersonation(target_service, lifetime)
    vertexai.init(
        project=project,
        location=location,
        credentials=c
    )