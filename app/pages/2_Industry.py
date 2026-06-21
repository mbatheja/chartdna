import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Industry - ChartDNA", page_icon="🎸", layout="wide")

st.title("🕴🏻Industry")
st.caption("Insights into billboard trends for you studio")

tab1, tab2, tab3 = st.tabs(["💓 Music Pulse", "🛟 Safe Bet", "👥 Cluster Analytics"])

with tab1:
    st.subheader("Your week in music summarized")

    if st.button("Generate Report"):
        with st.spinner("Composing..."):
            response = requests.get(f"{API_URL}/trend-report")
                    
            data = response.json()
            st.write(data["report"])

with tab2:
    if st.button("Get Recommendation"):
        with st.spinner("Shuffling..."):
            response = requests.get(f"{API_URL}/safe-bet")
                    
            data = response.json()
            st.write(data["recommendation"])

with tab3:
    with st.spinner("Clustering..."):
        response = requests.get(f"{API_URL}/clusters")       
        data = response.json()
        df = pd.DataFrame(data)
    
    st.bar_chart(df.set_index("cluster")["avg_rank"])
    st.dataframe(df, use_container_width=True)