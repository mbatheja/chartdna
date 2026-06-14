import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


load_dotenv()

DB_PATH = os.getenv("DB_PATH")


def load_tracks() -> pd.DataFrame:
    """
    Load dim_track table into a df. 
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
        SELECT track_name, artist_name, top_tags, total_tag_count
                      FROM dim_track
                      WHERE top_tags IS NOT NULL    
    """).fetchdf()
    conn.close()
    return df

def vectorize_tags(df: pd.DataFrame) -> tuple:
    """
    Convert track tags into tf-idf table where rows are tracks and columns are tags.
    tags are split into tokens on comma.
    """
    vectorizer = TfidfVectorizer(
        token_pattern = r"[^,]+",
        lowercase = True,
        max_features=200,
    )

    tag_strings = df["top_tags"].str.strip()
    tfidf_matrix = vectorizer.fit_transform(tag_strings)

    return tfidf_matrix, vectorizer


def find_optimal_clusters(tfidf_matrix, max_k: int = 15) -> dict:
    """
    Determines silhouette score iteratively for n_clusters from 2 to 15.
    """

    scores = {}
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf_matrix)
        score = silhouette_score(tfidf_matrix, labels)
        scores[k] = score
        print(f"  k={k}: silhouette={score:.3f}")
    return scores

def plot_silhouette_scores(scores: dict, output_path: str = "ml/silhouette_scores.png") -> None:
    """
    Plots graph for silhouette score vs number of clusters.
    """

    ks = list(scores.keys())
    values = list(scores.values())

    plt.figure(figsize=(8,5))
    plt.plot(ks, values, marker="o")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Silhouette score")
    plt.title("Silhouette score vs number of clusters")
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved silhouette plot to {output_path}")

def cluster_tracks(tfidf_matrix, n_clusters: int) -> list:
    """
    Predict cluster labels using Kmeans on track tag tfidf matrix.
    Args:
    tfidf_matrix: tidf matrix of track tags
    n_clusters: number of clusters determined as optimal from silhuoette score

    Return:
    Predicted cluster labels

    """
    kmeans = KMeans(
        n_clusters = n_clusters,
        random_state=42,
        n_init=10,
    )
    cluster_labels = kmeans.fit_predict(tfidf_matrix)
    return cluster_labels

def save_clusters(df: pd.DataFrame) -> None:
    """
    Save cluster assignment of tracks in df.
    """
    conn = duckdb.connect(DB_PATH)

    conn.execute("""
                 CREATE OR REPLACE TABLE ml_track_clusters AS
                 SELECT track_name, artist_name, top_tags, cluster, CURRENT_TIMESTAMP AS generated_at
                 FROM df
                 """)
    conn.close()
    print(f"{len(df)} tracks were assigned clusters")

def run():
    """
    Run helper functions.
    """
    df = load_tracks()
    print(f"Loaded {len(df)} tracks")

    tfidf_matrix, vectorizer = vectorize_tags(df)
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

    print("\nFinding optimal number of clusters...")
    scores = find_optimal_clusters(tfidf_matrix, max_k=15)
    plot_silhouette_scores(scores)

    best_k = max(scores, key=scores.get)
    print(f"\nBest k: {best_k} (silhouette={scores[best_k]:.3f})")

    labels = cluster_tracks(tfidf_matrix, n_clusters = best_k)
    df["cluster"] = labels

    save_clusters(df)

    for cluster_id in sorted(df["cluster"].unique()):
        cluster_tracks_df = df[df["cluster"] == cluster_id]
        print(f" --*-- Cluster {cluster_id}: {len(cluster_tracks_df)}  tracks --*--")
        print(cluster_tracks_df[["track_name", "top_tags"]].head(3))
    return df, scores

if __name__ == "__main__":
    run()