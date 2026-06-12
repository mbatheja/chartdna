select artist_name, CAST(listeners AS BIGINT) AS listener_count, CAST(playcount AS BIGINT) AS play_count, url, fetched_at, week_start
  from {{ source('lastfm', 'raw_artists')}}
 where artist_name IS NOT NULL