import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LastFmClient:
    BASE_URL = "https://ws.audioscrobbler.com/2.0/"

    def __init__(self):
        self.api_key = os.getenv("LASTFM_API_KEY")

        if not self.api_key:
            raise ValueError("LASTFM_API_KEY must be in .env")
              

    def get(self, method:str, params: dict = None) -> dict:
        base_params = {
            "method": method,
            "api_key": self.api_key,
            "format":"json",
        }
        if params:
            base_params.update(params)

        response = requests.get(self.BASE_URL, params=base_params)
        response.raise_for_status()
        return response.json()

    def get_top_tracks(self, limit: int=100) -> list[dict]:
        result = self.get("chart.getTopTracks", params={"limit": limit})
        return result.get("tracks",{}).get("track", [])

    def get_top_artists(self, limit: int=100) -> list[dict]:
        result = self.get("chart.getTopArtists", params={"limit": limit})
        return result.get("artists",{}).get("artist", [])

    def get_track_info(self, track_name:str, artist_name:str) -> list[dict]:
        result = self.get("chart.getTopArtists", params={
            "track": track_name,
            "artist": artist_name,
        })
        return result.get("track", {})

    def get_artist_info(self, artist_name: str) -> dict:
        result = self.get("artist.getInfo", params={"artist": artist_name})
        return result.get("artist", {})
    
    def get_artist_top_tracks(self, artist_name: str, limit: int = 10) -> list[dict]:
        result = self.get("artist.getTopTracks", params={
            "artist": artist_name,
            "limit": limit,
        })
        return result.get('toptracks', {}).get('track', [])
    
    def get_track_tags(self, track_name: str, artist_name: str) -> list[dict]:
        result = self.get('track.getTopTags', params={
            'track': track_name,
            'artist': artist_name,
        })
        return result.get('toptags', {}).get('tag', [])

if __name__ == "__main__":
    client = LastFmClient()

    print ('Top 5 Tracks')
    tracks = client.get_top_tracks(limit=5)
    for track in tracks:
        print(f"{track['name']} by {track['artist']['name']} - {track['playcount']} plays")

    print('Track Tags')
    tags = client.get_track_tags(tracks[0]['name'], tracks[0]['artist']['name'])
    for tag in tags[:5]:
        print(f" #{tag['name']} ({tag['count']})")

    print('Artist Info')
    artist = client.get_artist_info(tracks[0]['artist']['name'])
    print(f"Artist: {artist['name']}")
    print(f"Listeners: {artist['stats']['listeners']}")
    print(f"Play count: {artist['stats']['playcount']}")