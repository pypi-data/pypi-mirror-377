from pyschare.data_processing.embeddings_utils import get_embeddings
from pyschare.data_processing.vector_search_utils import vector_search_find_neighbors
from pyschare.data_processing.config import (
    PROJECT_ID, 
    LOCATION, 
    variable_index_info,
    target_service,
    lifetime)
import json 
from pyschare.chatbot.impersonation import get_storage_client

def download_json_from_gcs(file_index):
    """
    Download a JSON file from a Google Cloud Storage URI and return a list of Python dictionaries of its contents. 

    Args:
        gcs_uri (str): The GCS URI (e.g., 'gs://bucket-name/path/to/file.json').
    
    Returns:
        list: A list of Python dictionaries, each representing a JSON object from the file.
    """
    
    # Construct the filename based on the file index
    filename = f"{variable_index_info['embeddings_blob_name']}/{file_index}_embeddings.json"

    # Initialize the GCS client and download the file
    # client = storage.Client()
    # Added new
    client = get_storage_client(target_service, lifetime)
    #
    bucket = client.bucket(variable_index_info["bucket_name"])
    blob = bucket.blob(filename)
    content = blob.download_as_text()

    # Process the content to create a list of JSON objects
    lines = content.splitlines()

    # Each line is now a separate JSON chunk (as a string)
    json_chunks = [line for line in lines if line.strip()]

    # Parse each chunk into a Python dict:
    parsed_chunks = [json.loads(chunk) for chunk in json_chunks]

    return parsed_chunks


def get_neighbor_context(neighbor):
    """
    Fetches the context (metadata) for a given neighbor from the vector search results.
    
    Args:
        neighbor (aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor): The neighbor object containing the ID of the embedding.
    
    Returns:
        dict: The metadata associated with the neighbor's embedding.
    """

    # Each neighbor's ID is in the format "file_index-chunk_index"
    file_index = neighbor.id.split("-")[0]
    chunk_index = neighbor.id.split("-")[1]

    # fetch the embedding file
    embedding_file = download_json_from_gcs(file_index)

    # return metadata field from the specific chunk
    return embedding_file[int(chunk_index)]["metadata"]
    

def fetch_variable_context(user_query):
    """
    Searches the variable index for related hits to user query. 

    Args:
        user_query (str): The user's query for which context is to be fetched.

    Returns:
        str: The context retrieved for the user's query.
    """
    
    # Step 1. Embed user query 
    query_embedding = get_embeddings([user_query])
    # query_embedding = query_embeddings(user_query)

    # Step 2. Identify nearest neighbors in the vector search index
    response = vector_search_find_neighbors(
        project=PROJECT_ID,
        location=LOCATION,
        index_endpoint_name=variable_index_info["endpoint_name"],
        deployed_index_id=variable_index_info["endpoint_display_name"],
        queries=query_embedding,
        num_neighbors=5
    )

    # Step 3. Extract the context from each neighbor using a list comprehension
    text_responses = [get_neighbor_context(neighbor) for neighbor in response[0]]

    return text_responses 