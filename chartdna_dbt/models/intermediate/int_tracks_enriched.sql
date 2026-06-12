select st.track_name, st.artist_name, st.play_count, st.listener_count, ROUND(st.play_count/ NULLIF(st.listener_count, 0) ,2) as play_to_listener_ratio,
       st.rank, st.url, st.week_start, sa.listener_count AS artists_listener_count, sa.play_count as artist_play_count
  from {{ref('stg_tracks')}} as st left join {{ref('stg_artists')}} as sa using (artist_name)
