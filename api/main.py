from fastapi import FastAPI
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.trend_report import generate_trend_report
from llm.semantic_search import semantic_search
from llm.track_explainer import generate_track_explanation
from llm.safe_bet import generate_safe_bet
from llm.context import get_cluster_summary, get_anomalies_summary, DB_PATH


app = FastAPI(title="ChartDNA API", version="1.0")

@app.get("/trend-report")
def trend_report():
    result = generate_trend_report()
    return {"report": result}

@app.get("/search")
def search(q:str):
    result = semantic_search(q).to_dict(orient="records")
    return result

@app.get("/explain")
def explain(track:str, artist:str):
    result = generate_track_explanation(track, artist)
    return {"explanation": result}

@app.get("/safe-bet")
def safe_bet():
    result = generate_safe_bet()
    return {"recommendation": result}

@app.get("/clusters")
def cluster_summary():
    result = get_cluster_summary().to_dict(orient="records")
    return result

@app.get("/")
def health_check():
    return {"status":"ok", "app": "ChartDNA API", "version": "1.0"}



