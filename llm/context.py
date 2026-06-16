import os
import sys
import duckdb
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ml.anomaly_detection import load_tracks_with_clusters, z_score, find_anomalies

load_dotenv()

DB_PATH = os.getenv("DB_PATH")

def get_top_tracks(n: int=10) -> pd.DataFrame:
    """
    Fetch tracks ranked top 10 this week and load into a dataframe.
    """

    conn = duckdb.connect(DB_PATH)
    df = conn.execute(f"""
         SELECT track_name, artist_name, rank, play_count, play_to_listener_ratio, top_tags
           FROM fct_chart_entries
          ORDER BY rank ASC
          LIMIT {n}
                      """).fetchdf()
    conn.close()
    return df

def get_cluster_summary() -> pd.DataFrame:
    """
    Get a summary of tracks and average rank of tracks in a cluster.
    """
    
    conn = duckdb.connect(DB_PATH)
    df = conn.execute(
        """
    SELECT c.cluster, COUNT(*) AS track_count, 
           ROUND(AVG(f.rank), 2) AS avg_rank,
           ARG_MIN(c.top_tags, f.rank) AS sample_tags
      FROM fct_chart_entries AS f 
           LEFT JOIN ml_track_clusters AS c ON f.track_name = c.track_name
           AND f.artist_name = c.artist_name
     WHERE c.cluster IS NOT NULL
     GROUP BY c.cluster
     ORDER BY track_count DESC 
     """
    ).fetchdf()

    conn.close()
    return df

def get_anomalies_summary() -> pd.DataFrame:
    df = load_tracks_with_clusters()
    zscore_df = z_score(df)
    anomaly_df = find_anomalies(zscore_df, 2.0)
    return anomaly_df

if __name__ == "__main__":
    print("top tracks \n")
    print(get_top_tracks(5))
    print("cluster summary \n")
    print(get_cluster_summary())
    print("anomalies \n")
    print(get_anomalies_summary())
