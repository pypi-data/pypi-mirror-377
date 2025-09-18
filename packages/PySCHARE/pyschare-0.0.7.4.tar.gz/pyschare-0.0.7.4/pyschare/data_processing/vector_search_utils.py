from google.cloud import aiplatform


def vector_search_find_neighbors(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    queries: list[list[float]],
    num_neighbors: int,
) -> list[
    list[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]
]:
    """Query the vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_endpoint_name (str): Required. Index endpoint to run the query
        against.
        deployed_index_id (str): Required. The ID of the DeployedIndex to run
        the queries against.
        queries (List[List[float]]): Required. A list of queries. Each query is
        a list of floats, representing a single embedding.
        num_neighbors (int): Required. The number of neighbors to return.

    Returns:
        List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]] - A list of nearest neighbors for each query.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint.
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Query the index endpoint for the nearest neighbors.
    return my_index_endpoint.find_neighbors(
        deployed_index_id=deployed_index_id,
        queries=queries,
        num_neighbors=num_neighbors,
    )

