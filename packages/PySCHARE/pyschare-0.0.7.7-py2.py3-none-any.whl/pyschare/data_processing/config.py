# notebook_config.py

# GCP Project
PROJECT_ID = "schare-gemini"
LOCATION = "us-central1"
LLM_PROJECT_ID = "schare-gemini"
MODEL_NAME = "gemini-2.0-flash"


# Variable Index Info
variable_index_info = {
    "name": "variable-index",
    "ID": "839325395202342912",
    "bucket_name": "schare-rag-data",
    "embeddings_blob_name": "variables_preprocessed_json_embeddings",
    "embeddings_URI": "gs://schare-rag-data/variables_preprocessed_json_embeddings",
    "endpoint_name": "projects/289557206371/locations/us-central1/indexEndpoints/2050582588732473344",
    "endpoint_display_name": "variable_index_endpoint_1750777115598",
}

# SCHARE Bucket Name
RAG_DATA_BUCKET_NAME = "schare-rag-data"
COMBINED_EMBEDDINGS_FOLDER = "combined_embeddings"
COMBINED_FILE_NAME = "data_notebooks"

# Embedding Model Configurations
EMBEDDING_MODEL = "text-embedding-005"
BATCH_SIZE = 5
OUTPUT_DIM = 768
TASK = "RETRIEVAL_DOCUMENT"


short_term_history = "short_term_history.json"
max_history = 10
TOP_K = 5

lifetime = 1800
target_service = "rag-user@schare-gemini.iam.gserviceaccount.com"
