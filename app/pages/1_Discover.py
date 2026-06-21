import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Discover - ChartDNA", page_icon="🎸", layout="wide")

st.title("🎸Discover")
st.caption("Search for music by vibe, mood, or genre")

tab1, tab2 = st.tabs(["🔍 Search by Vibe", "💫 Hit Track Decoded?"])
with tab1:
    st.subheader("Song Search")

    query = st.text_input("What are you in the mood for?",
    placeholder =  "e.g. moody indie tracks, high energy dance music.... ")

    if query:
        with st.spinner("Hold On, I am flipping through the cd stack..."):
            response = requests.get(f"{API_URL}/search", params={"q": query})
            results = response.json()

        for r in results[:5]:
            with st.container(border=True):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**{r['track_name']}**")
                    st.caption(r['artist_name'])
                    st.caption(r['top_tags'])
                    with col2:
                        st.metric("Match",f"{r['similarity_score']:.0%}")

with tab2:
    st.subheader("Why is a track charting?")

    track_input = st.text_input("Track name", placeholder="e.g. the cure")
    artist_input = st.text_input("Artist name", placeholder="e.g. Olivia Rodrigo")

    if st.button("Explain"):
        if track_input and artist_input:
            with st.spinner("Analyzing..."):
                response = requests.get(f"{API_URL}/explain",
                                            params = {"track": track_input, "artist": artist_input})
                    
                data = response.json()

                if "explanation" in data: #safety check to see if need to display explanation
                    with st.container(border=True):
                        st.markdown(f"**{track_input}** by {artist_input}")
                        st.write(data["explanation"])
                else:
                    st.error("Track not found - check the spelling and try again")
                
        else:
            st.warning("Please enter both track name and artist name")
                    