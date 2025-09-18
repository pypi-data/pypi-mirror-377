from pyschare.data_processing.config import (
    COMBINED_EMBEDDINGS_FOLDER,
    COMBINED_FILE_NAME,
    RAG_DATA_BUCKET_NAME,
    TOP_K,
    target_service, 
    lifetime
)
from pyschare.data_processing.embeddings_utils import query_embeddings
from pyschare.chatbot.retrieve_text import fetch_variable_context
from pyschare.chatbot.impersonation import get_storage_client

import numpy as np
import json



# Simple in-memory cache to replace Streamlit session state
_embedding_cache = {}

## Another version of step 1 to download the file from GCS and keep in cache memory
def download_json_file(file_name):
    """
    Download and cache embedding file from GCS
    """

    cache_key = f"{file_name}_embeddings"

    # Check if already cached
    if cache_key not in _embedding_cache:
        # Construct the filename based on the file index
        filename = f"{COMBINED_EMBEDDINGS_FOLDER}/{file_name}_embeddings.json"

        # Initialize the GCS client and download the file
        # client = storage.Client()
        # Added new
        client = get_storage_client(target_service, lifetime)
        #
        bucket = client.bucket(RAG_DATA_BUCKET_NAME)
        blob = bucket.blob(filename)
        content = blob.download_as_text()

        # Parse and store in cache
        _embedding_cache[cache_key] = json.loads(content)

    return _embedding_cache[cache_key]



## Step 2
# Query embeddings for the user question
# Importing the `from data_processing.embeddings_utils import query_embeddings`


## Step 3
# Create the ditance measure function (Cosine, Dot)
def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# Step 4
# Retrieve the top N results based on the distance measure
# Return the top chunks
def retrieve_top_k(query_embedding, stored_embeddings, top_k=TOP_K):
    """
    Find top-k most similar chunks to the query embedding.
    """
    scored_chunks = []

    for item in stored_embeddings:
        score = cosine_similarity(query_embedding, item["embedding"])
        scored_chunks.append((score, item))

    # Sort by highest similarity score
    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    # Return top-k chunks
    top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]
    return top_chunks

# Step 5
# Get the metadata from the chunks and combine them to feed the Gemini

def dict_to_text(dict_data):
    """
    Convert a dictionary to a formatted string.
    """
    lines = [f"{key}: {value}" for key, value in dict_data.items()]
    return "\n".join(lines)


def data_notebook_context(chunks):
    """
    Combine the context from the top chunks into a single string.
    """
    combined_context = ""
    for chunk in chunks:
        # Extract relevant metadata
        metadata = chunk.get("metadata", {})
        if not metadata:
            continue # Skip if no metadata is available

        # # Collect all metadata lines for this chunk
        txt_block = dict_to_text(metadata)

        combined_context += f"{txt_block}\n\n"

    return combined_context


# Step 6
# Get the top k chunk from the latest index endpoint for variables
def variable_context(query):
    # get top match from the index  as a list
    top_chunk_list = fetch_variable_context(query)

    text_block = ""

    for item in top_chunk_list:
        dataset = item.get("Dataset", "Unknown Dataset")
        variable = item.get("Variable", "Unknown Variable")
        description = item.get("Description", "No Description")

        # Combine into simple, flat text
        text_block += f"Dataset: {dataset}\nVariable: {variable}\nDescription: {description}\n\n"

    return text_block


def get_context_hybrid(query, COMBINED_FILE_NAME, top_k=5): 
    # Step 1: Download the combined embeddings JSON file
    json_file = download_json_file(COMBINED_FILE_NAME)  
    # Step 2: Get the query embedding
    query_embedding = query_embeddings(query)

    # Step 3: Retrieve top-k chunks
    top_chunks = retrieve_top_k(query_embedding, json_file, top_k)

    # Step 4: context from data list and notebooks
    context_from_data = data_notebook_context(top_chunks)

    # Step 5: context from variable metadata
    context_from_variables = variable_context(query)

    # Step 6: Combine both contexts
    combined_context = f"{context_from_data}\n\n{context_from_variables}"

    return combined_context

if __name__ == "__main__":
    # query = "What is the latest BRFSS dataset available?"
    # query = "Notebook to teach about python basics"
    query = "Which datasets have variables about obesity?"
    combined_context = get_context_hybrid(query, COMBINED_FILE_NAME, top_k=5)
    print(f"Final combined context:\n{combined_context}")