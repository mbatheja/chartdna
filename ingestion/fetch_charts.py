import duckdb
from datetime import datetime, timedelta
from ingestion.lastfm_client import LastFmClient
from ingestion.database import get_connection, create_tables

def get_week_start() -> datetime.date:
    """Calculate current week's Monday."""
    today = datetime.today()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    return monday.date()

def fetch_and_store_tracks(conn: duckdb.DuckDBPyConnection,
                           client: LastFmClient,
                           week_start: datetime.date,
                           limit: int = 100) -> list[dict]:
    """ Fetch and Populate top tracks for the week in the raw tracks table """    
    print(f"Loading top {limit} tracks for the week {week_start}...")
    tracks = client.get_top_tracks(limit=limit)

    fetched_at = datetime.now()
    rows = []

    for rank, track in enumerate(tracks, start=1):
        row = {
            "track_name": track.get("name"),
            "artist_name": track.get("artist", {}).get("name"),
            "playcount": int(track.get("playcount", 0)),
            "listeners": int(track.get("listeners", 0)),
            "url": track.get("url"),
            "rank": rank,
            "fetched_at": fetched_at,
            "week_start": week_start,
        }
        rows.append(row)
    
    conn.executemany("""
        INSERT INTO raw_tracks
        (track_name, artist_name, playcount, listeners, url, rank, fetched_at, week_start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [list(r.values()) for r in rows])

    print(f" Inserted {len(rows)} tracks")
    return rows

def fetch_and_store_artists(conn: duckdb.DuckDBPyConnection,
                            client: LastFmClient,
                            tracks: list[dict],
                            week_start: datetime.date,
                               ) -> list[dict]:

    """Fetch and store records oif artists with popular tracks"""
    print(f"Fetching artist info for {len(tracks)} artists...")

    seen_artists = set()
    rows = []
    fetched_at = datetime.now()

    for track in tracks:
        artist_name = track["artist_name"]

        if artist_name in seen_artists:
            continue
        seen_artists.add(artist_name)

        try:
            artist = client.get_artist_info(artist_name)
            row = {
                "artist_name": artist.get("name"),
                "listeners": int(artist.get("stats", {}).get("listeners", 0)),
                "playcount": int(artist.get("stats", {}).get("playcount", 0)),
                "url": artist.get("url"),
                "fetched_at": fetched_at,
                "week_start": week_start,
            }
            rows.append(row)
        except Exception as e:
            print(f"Skipping artist {artist_name}: {e}")
            continue
        
    conn.executemany("""
        INSERT INTO raw_artists
        (artist_name, listeners, playcount, url, fetched_at, week_start)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [list(r.values()) for r in rows])

    print(f" Inserted {len(rows)} artists")
    

def fetch_and_store_tags(conn: duckdb.DuckDBPyConnection,
                           client: LastFmClient,
                           tracks: list[dict], 
                           week_start: datetime.date,
                           limit: int = 100) -> list[dict]:
    """ Populate and store artist and track tags and metrics."""
    print(f"Fetching tags for {len(tracks)} tracks ...")

    rows = []
    fetched_at = datetime.now()

    for track in tracks:
        track_name = track["track_name"]
        artist_name = track["artist_name"]

        try:
            tags = client.get_track_tags(track_name, artist_name)

            if not tags:
                continue

            for tag in tags:
                row = {
                    "track_name": track_name,
                    "artist_name": artist_name,
                    "tag_name": tag.get("name"),
                    "tag_count": int(tag.get("count", 0)),
                    "fetched_at": fetched_at,
                    "week_start": week_start,
                }
                rows.append(row)

        except Exception as e:
            print(f"Skipping tags for {track_name}: {e}")
            continue

        if rows: # to prevent executemany from throwing error in DuckDB if list is empty (in case some tracks have no tags)
            conn.executemany("""
INSERT INTO raw_track_tags
                             (track_name, artist_name, tag_name, tag_count, fetched_at, week_start)
                             VALUES (?, ?, ?, ?, ?, ?)
                             """, [list(r.values()) for r in rows])

        print(f" Inserted {len(rows)} tags")


def run(limit: int = 100) -> None:
    """orchestrate function calls - db connection, fetch and store tracks, artists and tags"""
    client = LastFmClient()
    conn = get_connection()
    try:
        create_tables(conn)

        week_start = get_week_start()
        print(f"Starting ingestion for week of {week_start}")

        existing = conn.execute("""
SELECT COUNT(*) FROM raw_tracks WHERE week_start = ?
""", [week_start]).fetchone()[0]

        if existing > 0:
            print(f"Data for week {week_start} already exists ({existing} rows). Skipping.")
            return

        tracks = fetch_and_store_tracks(conn, client, week_start, limit)
        fetch_and_store_artists(conn, client, tracks, week_start)
        fetch_and_store_tags(conn, client, tracks, week_start)

        print(f"Ingestion complete for week of {week_start}")
    finally:
        conn.close()

if __name__ == "__main__":
    run(limit=100)