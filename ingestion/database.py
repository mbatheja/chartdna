import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/chartdna.duckdb")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH)

def create_tables(conn):
    conn.execute("""
       CREATE TABLE IF NOT EXISTS raw_tracks (
                 track_name    VARCHAR,
                 artist_name   VARCHAR,
                 playcount     BIGINT,
                 listeners     BIGINT,
                 url           VARCHAR,
                 rank          INTEGER,
                 fetched_at    TIMESTAMP, 
                 week_start    DATE
                 )
                 """)
    conn.execute("""
CREATE TABLE IF NOT EXISTS raw_artists (
                 artist_name    VARCHAR,
                 listeners    BIGINT,
                 playcount    BIGINT,
                 url    VARCHAR,
                 fetched_at    TIMESTAMP,
                 week_start    DATE
                 )
            """)
    conn.execute("""
CREATE TABLE IF NOT EXISTS raw_track_tags (
                 track_name    VARCHAR,
                 artist_name    VARCHAR,
                 tag_name    VARCHAR,
                 tag_count    INTEGER,
                 fetched_at    TIMESTAMP,
                 week_start     DATE
                 )
            """)
    print('Tables created successfully')

if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)

    result = conn.execute('SHOW TABLES').fetchall()
    print('Tables in database:')
    for table in result:
        print(f"{table[0]}")

    conn.close()