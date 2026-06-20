import streamlit as st

st.set_page_config(page_title="ChartDNA Home", page_icon="🎸", layout="wide")
st.markdown("""
<style>
            .block-container {padding-top: 2rem;
            h1 { color: #00c9a7; font-size: 3rem;}
            h2 { color: #00c9a7;}
             .stDriver {border-color: #00c9a7;}
            </style>
            """, unsafe_allow_html=True)


st.title(" 🎸Chart DNA 🧬")
st.subheader("Decode the anatomy of songs that ruke the Billboard")

st.markdown ("""
             ChartDNA is a music intelligence platform powered by Last.fm chart data,
             ML clustering, and LLM analysis.
             
             **Choose a page from the sidebar:**

            - ▶️ **Discover** — search for music by vibe, explore similar tracks, understand why songs chart
            - 👩🏻‍💼 **Industry** — weekly trend reports, safe bet recommendations, cluster analytics
        """)

st.divider()
st.caption("Data updates weekly via Airflow • Powered by Last.fm, OpenAI, dbt, DuckDB")

