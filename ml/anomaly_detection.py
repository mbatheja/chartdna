import duckdb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def load_tracks_with_clusters() -> pd.DataFrame:
    """
    Create a table in duckdb that join metrics with 
    clustering table and loads data into a df for 
    further analysis.
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
                      SELECT f.track_name, f.artist_name, f.rank, f.play_count,
                             f.listener_count, f.play_to_listener_ratio, c.cluster
                        FROM fct_chart_entries AS f
                             LEFT JOIN ml_track_clusters AS c ON f.track_name = c.track_name 
                             AND f.artist_name = c.artist_name
                      """).fetchdf()
    conn.close()
    return df

def z_score(df) -> pd.DataFrame:
    """Calculates z-score for play_to_listener_ratio tracks. 
    z-score is calculated based on cluster average and
    standard deviation for play_to_listener_ratio."""
    df = df.dropna(subset=["cluster"])
    df["cluster_size"] = df.groupby("cluster")["play_to_listener_ratio"].transform("size")
    df["cluster_mean"] = df.groupby("cluster")["play_to_listener_ratio"].transform("mean")
    df["cluster_stdev"] = df.groupby("cluster")["play_to_listener_ratio"].transform("std")
    df["z_score"] = ((df["play_to_listener_ratio"] - df["cluster_mean"]) / df["cluster_stdev"]).round(3)
    df = df[df["cluster_size"] >= 4]
    return df[["cluster", "track_name", "artist_name", "rank", "play_count", "listener_count", "cluster_mean", "cluster_stdev", "z_score"]]

def find_anomalies(df: pd.DataFrame, threshold: float = 2.0):
    """ Find anomaly tracks with an absolute z-score higher than 
    threshold and sort tracks in descending order of z-score."""
    anomalies = df[df["z_score"].abs() > threshold]
    return anomalies.sort_values("z_score", ascending = False)

def run():
    df = load_tracks_with_clusters()
    z_score_df = z_score(df)
    print(f"Z-score dataframe: {len(z_score_df)} tracks \n {z_score_df}")    
    anomalies = find_anomalies(z_score_df, threshold=2.0)
    print(f"Anomaly dataframe: {len(anomalies)} tracks \n {anomalies}")

if __name__ == "__main__":
    run()

