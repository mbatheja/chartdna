select MAX(week_start) as last_week, track_name, artist_name, top_tags, url
  from {{ref('fct_chart_entries')}}
 group by track_name, artist_name, top_tags, url