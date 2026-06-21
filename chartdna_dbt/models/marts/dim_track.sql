select MAX(week_start) as last_week, track_name, artist_name, 
       ARG_MAX(top_tags, week_start) AS top_tags,
       ARG_MAX(url, week_start) AS url,
       ARG_MAX(total_tag_count, week_start) AS total_tag_count
  from {{ref('fct_chart_entries')}}
 group by track_name, artist_name