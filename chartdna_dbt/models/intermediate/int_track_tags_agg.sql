with unique_tags as (
  select track_name, artist_name, week_start, tag_name, 
  max(tag_count) as tag_count
  from {{ref('stg_track_tags')}}
 group by track_name, artist_name, week_start, tag_name
)
select track_name, artist_name, week_start, 
sum(tag_count) as total_tag_count, 
string_agg(tag_name, ', ' ORDER BY tag_count DESC) AS top_tags
  from unique_tags
 group by track_name, artist_name, week_start
