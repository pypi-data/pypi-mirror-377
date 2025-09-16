# embeddings.py

import json
from fastapi import HTTPException
from sqlalchemy import text
from typing import List, Dict, Any
from oak.main import get_db_session
from fastembed import TextEmbedding

# Initialize the embedding model outside of the function to load it once
# and reuse it for all subsequent calls. This is crucial for performance.
try:
    # A common model is 'BAAI/bge-small-en-v1.5'
    # It is lightweight, fast, and performs well for RAG.
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("INFO: FastEmbed model loaded successfully.")
except Exception as e:
    print(f"ERROR: Failed to load FastEmbed model: {e}")
    embedding_model = None

def get_query_embedding(text: str) -> List[float]:
    """
    Generates a vector embedding for the input text using the FastEmbed library.

    Args:
        text: The input text to be embedded.

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        ValueError: If the text is empty or the embedding model is not loaded.
    """
    if embedding_model is None:
        raise ValueError("Embedding model is not initialized.")
    if not text:
        raise ValueError("Input text cannot be empty.")

    # The embed method returns a generator. We take the first item.
    embedding = list(embedding_model.embed(texts=[text]))[0]

    # Convert numpy array to a list of floats for database insertion
    return embedding.tolist()


def search_embeddings(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Performs a vector similarity search in the text_embeddings table.

    Args:
        query_text: The text to search for, which will be converted to a vector.
        top_k: The number of top similar results to retrieve.

    Returns:
        A list of dictionaries containing the most similar text chunks and their
        distance from the query vector.

    Raises:
        HTTPException: If the embedding generation or database query fails.
    """
    if not isinstance(top_k, int) or top_k <= 0:
        raise HTTPException(status_code=400, detail="`top_k` must be a positive integer.")

    try:
        # Step 1: Generate the embedding vector for the query text
        query_vector = get_query_embedding(query_text)

        # Step 2: Perform the vector similarity search in the database
        with get_db_session() as conn:
            query = text("""
                SELECT
                    id,
                    content_text,
                    source_type,
                    source_id,
                    metadata,
                    embedding <=> :query_vector AS distance
                FROM text_embeddings
                ORDER BY distance
                LIMIT :k
            """)

            query_vector_str = json.dumps(query_vector)

            result = conn.execute(query, {"query_vector": query_vector_str, "k": top_k})

            formatted_results = [
                {
                    "content_text": row.content_text,
                    "distance": row.distance,
                    "source_id": row.source_id,
                    "metadata": row.metadata
                }
                for row in result.fetchall()
            ]

        return formatted_results

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform vector search: {str(e)}")


if __name__ == "__main__":
    try:
        test_query = "What are the latest stock market trends?"
        test_top_k = 5

        print(f"Searching for embeddings similar to: '{test_query}'")
        results = search_embeddings(test_query, test_top_k)

        print(json.dumps(results, indent=2))

    except HTTPException as he:
        print(f"Error: {he.detail}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")