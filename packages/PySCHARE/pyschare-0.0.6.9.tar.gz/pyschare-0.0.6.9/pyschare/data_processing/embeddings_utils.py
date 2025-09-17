# embeddings_utils.py
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from pyschare.data_processing.config import EMBEDDING_MODEL, OUTPUT_DIM, BATCH_SIZE, TASK
import time


def get_embeddings(texts: list[str]) -> list[list[float]]:

    embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):  # BATCH_SIZE = 5 from config.py
        time.sleep(1)  # to avoid the quota error

        # The dimensionality of the output embeddings.
        dimensionality = OUTPUT_DIM  # 768 form config.py

        # The task type for embedding. Check the available tasks in the model's documentation.
        task = TASK  # "RETRIEVAL_DOCUMENT" from config.py


        model = TextEmbeddingModel.from_pretrained(
            EMBEDDING_MODEL
        )  # EMBEDDING_MODEL=text-embedding-005 from config.py

        inputs = [
            (
                TextEmbeddingInput(text["content"], task)
                if isinstance(text, dict) and "content" in text
                else TextEmbeddingInput(text, task)
            )
            for text in texts[i : i + BATCH_SIZE]
        ]

        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        response = model.get_embeddings(inputs, **kwargs)

        embeddings = embeddings + [e.values for e in response]

    return embeddings


# to create embeddings for the query only
def query_embeddings(text):
    # Initialize the model
    model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    # Prepare input
    input_data = (
        TextEmbeddingInput(text["content"], TASK)
        if isinstance(text, dict) and "content" in text
        else TextEmbeddingInput(text, TASK)
    )

    # Set output dimensionality if defined
    kwargs = {"output_dimensionality": OUTPUT_DIM} if OUTPUT_DIM else {}

    # Get embeddings
    response = model.get_embeddings([input_data], **kwargs)

    return response[0].values