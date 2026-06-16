import duckdb
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from llm.context import get_cluster_summary, get_anomalies_summary, DB_PATH

load_dotenv()

def get_track_context(track_name: str, artist_name: str) -> dict:
    """
    
    """
    conn = duckdb.connect(DB_PATH)
    track_row = conn.execute("""

        SELECT  f.track_name, f.artist_name, f.rank, f.play_count, f.play_to_listener_ratio, 
                      c.cluster, f.top_tags
          FROM fct_chart_entries AS f 
               LEFT JOIN ml_track_clusters AS c
               ON f.track_name = c.track_name AND
                  f.artist_name = c.artist_name
         WHERE f.track_name = ? AND f.artist_name = ?
            
        """, [track_name, artist_name]).fetchdf()
    conn.close()
    
    if track_row.empty:
        return {"error": f"Track not found: {track_name} by {artist_name}"}
    
    track = track_row.iloc[0]
    
    clusters = get_cluster_summary()
    cluster_row = clusters[clusters["cluster"] == track["cluster"]]
    cluster_avg_rank = cluster_row.iloc[0]["avg_rank"]

    anomalies =  get_anomalies_summary()
    track_anomaly = anomalies[(anomalies["track_name"] == track_name)
                              & (anomalies["artist_name"] == artist_name)
                              ]
    is_anomaly = not track_anomaly.empty
    z_score = track_anomaly.iloc[0]["z_score"] if is_anomaly else None

    return {
        "track_name": track["track_name"], "artist_name" : track["artist_name"], 
                "rank": int(track["rank"]), "play_count": int(track["play_count"]), 
                "play_to_listener_ratio": float(track["play_to_listener_ratio"]), "top_tags": track["top_tags"], 
                "cluster" : int(track["cluster"]), "cluster_avg_rank": float(cluster_avg_rank), 
                "is_anomaly": is_anomaly, "z_score": float(z_score) if z_score is not None else None,
    }


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_track_explanation(track_name: str, artist_name: str) -> str:
    context = get_track_context(track_name, artist_name)
    if "error" in context:
        return context["error"]
    response = client.chat.completions.create(
               model = "gpt-4o-mini",
               messages = [{"role":"system", "content": f"""You are a seasoned analyst in the music industry. Provide analysis"
               "of '{track_name}' by '{artist_name}' current chart position. Give a concise and clearly worded analysis not exceeding 200 words."""},
                           {"role":"user", "content": f"""Create an explanation for the performance of the track in {context} outlining:
                            1. What led to the current status of the track (rank: {context['rank']}, play-to-listener ratio: {context['play_to_listener_ratio']})
                            2. How it compares to its cluster peers (cluster avg rank: {context['cluster_avg_rank']})
                            3. Whether anything unusual is happening (anomaly: {context['is_anomaly']}, z-score: {context['z_score']})
                            """}]
    )
    return response.choices[0].message.content

def save_explanation(explanation:str):
    """
    Cache explanation in duckdb.
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
                    CREATE OR REPLACE TABLE llm_track_explanation AS
                    SELECT ? AS explanation_text, CURRENT_TIMESTAMP AS generated_at
    """, [explanation])
    conn.close()


if __name__ == "__main__":
    explanation = generate_track_explanation("the cure", "Olivia Rodrigo")
    print(explanation)
    save_explanation(explanation)
    print("\nSaved to llm_track_explanation")