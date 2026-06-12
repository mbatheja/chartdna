select track_name, artist_name, tag_name, CAST(tag_count AS INT) AS tag_count , fetched_at, week_start
  from {{source('lastfm', 'raw_track_tags')}}
 where track_name IS NOT NULL AND artist_name IS NOT NULL and tag_name IS NOT NULL