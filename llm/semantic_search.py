import os
import sys
import duckdb
import pandas as pd
import numpy as np
import json
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ml.tag_clustering import load_tracks
from llm.context import DB_PATH

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list:
    """
    Convert input text into embedding using text-embedding-3-small model and open AI
    API.
    """
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def generate_track_embeddings() -> pd.DataFrame:
    """
    Generate embeddings from top tags of each track.
    """
    tracks = load_tracks()
    embeddings = []
    for idx, row in tracks.iterrows():
        embedding = get_embedding(row["top_tags"])
        embeddings.append(json.dumps(embedding))
        print(f"  {idx+1}/{len(tracks)}: {row['track_name']}")

    tracks["embedding"] = embeddings
    return tracks[["track_name", "artist_name", "top_tags", "embedding"]] 
    
def save_embeddings(df: pd.DataFrame) -> None:
    """
    Load embeddings to duckdb.
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
                CREATE OR REPLACE TABLE llm_track_embeddings AS
                SELECT track_name, artist_name, top_tags, embedding, CURRENT_TIMESTAMP AS generated_at
                FROM df
""")
    conn.close()

def load_embeddings() -> pd.DataFrame:
    """
    Load track embeddings from DuckDB and parse them from JSON strings into lists.
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
                    SELECT track_name, artist_name, top_tags, embedding
                      FROM llm_track_embeddings
                      """                                                                                                                                                                                                                                                                                                                                                                                        ).fetchdf()
    df["embedding"] = df["embedding"].apply(json.loads)
    conn.close()
    return df

def semantic_search(query: str, top_n: int = 5) -> pd.DataFrame:
    """
    Find cosine similarity score for track tags and user query and find n best matches
    """
    query_embedding = get_embedding(query)
    df = load_embeddings()
    track_matrix = np.array(df["embedding"].tolist())
    similarities = cosine_similarity([query_embedding], track_matrix)[0]
    df["similarity_score"] = similarities
    return df[["track_name", "artist_name", "top_tags", "similarity_score"]].sort_values("similarity_score", ascending=False).head(top_n)

def run():
    """
    Refresh embeddings for all tracks (called weekly by Airflow).
    """
    embedding_df = generate_track_embeddings()
    save_embeddings(embedding_df)
    print(f"\nSaved {len(embedding_df)} embeddings to llm_track_embeddings")

if __name__ == "__main__":
    results = semantic_search("moody indie tracks", top_n = 5)
    print(results)

