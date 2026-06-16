import os
import sys
import duckdb
from openai import OpenAI
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from llm.context import get_top_tracks,  get_cluster_summary, get_anomalies_summary, DB_PATH

load_dotenv()

def build_context_summary() -> str:
    top_tracks = get_top_tracks(10)
    clusters = get_cluster_summary()
    anomalies = get_anomalies_summary()
    summary = f"""
    TOP 10 TRACKS THIS WEEK:
    {top_tracks.to_string(index=False)}

    CLUSTER BREAKDOWN:
    {clusters.to_string(index=False)}

    ANOMALIES:
    {anomalies.to_string(index=False)}
    """

    return summary

def generate_trend_report() -> str:
    context = build_context_summary()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model ="gpt-4o-mini",
        messages=[
            {"role":"system", "content":"You are a seasoned analyst working in the"
            " music industry. You are to create a weekly musical report for executives in the music industry "
            "outlining trends and actual numbers from data. In a clear and concise manner"
            "draft a report with no more than 3-4 paragraphs."},
            {"role":"user", "content":f"""Create a weekly musical update report consisting of themes:"
            "1. Weekly chart toppers"
            "2. Notable patterns across clusters"
            "3. Anomalies and what they might mean."
            "Use this data for the report: ```{context}```"""}
        ]
    )
    return response.choices[0].message.content

def save_trend_report(report: str) -> None:
    """
    Cache weekly trend report in duckdb
    """
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("""
                    CREATE OR REPLACE TABLE llm_trend_report AS
                    SELECT ? AS report_text, CURRENT_TIMESTAMP AS generated_at
    """, [report])
    conn.close()



if __name__ == "__main__":
    report = generate_trend_report()
    print(report)
    save_trend_report(report)
    print("\nSaved to llm_trend_report table")