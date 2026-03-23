-- Example Analytical Queries for NFL Analytics

-- 1. Games by season and week with margin
SELECT season, week, home_team, away_team, home_score, away_score, margin, total
FROM games
WHERE season = 2023
ORDER BY week, game_id;

-- 2. Average score by team (home and away)
SELECT
  team,
  COUNT(*) AS games,
  AVG(pts) AS avg_ppg
FROM (
  SELECT home_team AS team, home_score AS pts FROM games
  UNION ALL
  SELECT away_team AS team, away_score AS pts FROM games
) t
GROUP BY team
ORDER BY avg_ppg DESC;

-- 3. Spread accuracy: how often home team covered
SELECT
  season,
  COUNT(*) AS games,
  SUM(CASE WHEN margin + spread_line > 0 THEN 1 ELSE 0 END) AS home_cover,
  AVG(ABS(margin + spread_line)) AS avg_line_error
FROM games
WHERE spread_line IS NOT NULL
GROUP BY season;

-- 4. Over/Under hit rate by season
SELECT
  season,
  COUNT(*) AS games,
  SUM(CASE WHEN total > total_line THEN 1 ELSE 0 END) AS overs,
  SUM(CASE WHEN total < total_line THEN 1 ELSE 0 END) AS unders
FROM games
WHERE total_line IS NOT NULL
GROUP BY season;

-- 5. High-scoring plays (explosive plays)
SELECT game_id, posteam, down, ydstogo, yardline_100, yards_gained, play_type
FROM plays
WHERE yards_gained >= 20
  AND season = 2023
ORDER BY yards_gained DESC
LIMIT 50;
