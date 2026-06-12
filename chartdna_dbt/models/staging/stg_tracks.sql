select track_name, artist_name, 
CAST(playcount AS BIGINT) AS play_count, 
CAST(listeners AS BIGINT) AS listener_count,
url,
rank,
fetched_at,
week_start 
  from {{source('lastfm','raw_tracks')}}
 where track_name IS NOT NULL AND artist_name IS NOT NULL
