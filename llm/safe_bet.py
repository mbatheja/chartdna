import os
import duckdb
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from llm.context import DB_PATH

def get_safe_bet_context() -> str:
    """
    Pull columns and create metrics to evaluate safe bet tracks.
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
    WITH track_weeks AS (
                     SELECT track_name, artist_name, COUNT(DISTINCT week_start) AS week_on_chart
                       FROM fct_chart_entries
                      GROUP BY track_name, artist_name 
    )
                      
SELECT c.cluster,
       COUNT(*) AS track_count, 
       AVG(f.rank) AS avg_rank, 
       ROUND(STDDEV(f.rank), 2) AS rank_variance,
       COUNT(DISTINCT f.artist_name) AS unique_artists,
       ROUND(COUNT(*) * 1.0/ COUNT(DISTINCT f.artist_name), 2) AS tracks_per_artist,
       ROUND(AVG(t.week_on_chart), 2) AS avg_weeks_on_chart,
       ARG_MIN(c.top_tags, f.rank) AS sample_tags
       
  FROM fct_chart_entries AS f 
       LEFT JOIN ml_track_clusters AS c ON f.track_name = c.track_name AND f.artist_name = c.artist_name
       LEFT JOIN track_weeks AS t ON t.track_name = c.track_name AND t.artist_name = c.artist_name
 WHERE c.cluster IS NOT NULL
 GROUP BY c.cluster
HAVING COUNT(*) >= 4
 ORDER BY avg_rank ASC
 LIMIT 5
""").fetchdf().to_string(index=False)
    return df

def generate_safe_bet() -> str:
    """ Generate explanation and strategic recommendation for music studios on the next assured hit given current trends """
    context = get_safe_bet_context()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages =[
        {"role":"system","content": f"""You are a senior A&R analyst, strategic and data-driven"
        "in nature. Your goal is to analyze chart data and advise with explanation what kind of music"
        "would be a sure hit for studios in the near future. Generate clear and concise analysis 
        not exceeding 2-3 sentences."""},
        {"role":"user", "content": f"""Generate recommendations on music that is likely to
          be a safe bet investment for studios based on this chart data {context} . Cover the following:
         1. the context
         2. Recommendation covering genre direction
         3. Sonic characteristics
         4. Target demographic
         5. Reason for why this is a low-risk safe bet right now"""}]
)
    return response.choices[0].message.content



if __name__ == "__main__":
    print(generate_safe_bet())
