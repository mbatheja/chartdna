import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tag_clustering import load_tracks, vectorize_tags

def compute_similarity_matrix(tfidf_matrix):
    """
    Computes cosine similarity from tf-idf matrix
    of track tags.
    """
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

def find_similar_tracks(df: pd.DataFrame, similarity_matrix, track_name: str, artist_name: str, top_n: int = 5 ) -> pd.DataFrame:
    """
    Finds the top_n tracks most similar to a given track based on cosine similarity of tag vectors.

    Args:
        df: tracks dataframe with track_name, artist_name, top_tags columns
        similarity_matrix: precomputed cosine similarity matrix
        track_name: name of the track to find similar tracks for
        artist_name: artist of the track (disambiguates same-named tracks)
        top_n: number of similar tracks to return

    Returns:
        DataFrame of similar tracks with similarity_score, sorted descending
    """
    matches = df[(df["track_name"] == track_name) & (df["artist_name"] == artist_name)]

    if matches.empty:
        print(f"Track not found: {track_name} by {artist_name}")
        return pd.DataFrame()
    
    track_idx = matches.index[0]
    similarity_scores = similarity_matrix[track_idx]
    similar_indices = similarity_scores.argsort()[::-1]
    similar_indices = [i for i in similar_indices if i != track_idx][: top_n]
    
    results = df.iloc[similar_indices][["track_name", "artist_name", "top_tags"]].copy()
    results["similarity_score"] = similarity_scores[similar_indices]

    return results

if __name__ == "__main__":
    df = load_tracks()
    tfidf_matrix, vectorizer = vectorize_tags(df)
    similarity_matrix = compute_similarity_matrix(tfidf_matrix)

    sample = df.iloc[0]
    print(f"Finding tracks similar to: {sample['track_name']} by {sample['artist_name']}")
    print(f"Tags: {sample['top_tags']} \n")

    similar = find_similar_tracks(
        df, similarity_matrix,
        track_name = sample["track_name"],
        artist_name = sample["artist_name"],
        top_n = 5
    )

    print(similar)