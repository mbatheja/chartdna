select
    ite.track_name,
    ite.artist_name,
    ite.week_start,
    ite.rank,
    ite.play_count,
    ite.listener_count,
    ite.play_to_listener_ratio,
    ite.artists_listener_count,
    ite.artist_play_count,
    ite.url,
    ita.top_tags,
    ita.total_tag_count
  from {{ref('int_tracks_enriched')}} as ite left join {{ref('int_track_tags_agg')}} as ita on ite.track_name = ita.track_name and ite.artist_name = ita.artist_name and ite.week_start = ita.week_start