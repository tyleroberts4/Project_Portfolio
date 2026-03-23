-- NFL Analytics Database Schema
-- For play-by-play, games, schedules, and betting lines

DROP SCHEMA IF EXISTS `nfl_analytics`;
CREATE SCHEMA `nfl_analytics`;
USE `nfl_analytics`;

-- TEAMS reference table
CREATE TABLE `teams` (
  `team_abbr` VARCHAR(10) NOT NULL,
  `team_name` VARCHAR(60) NULL,
  PRIMARY KEY (`team_abbr`)
);

-- GAMES: schedule and results
CREATE TABLE `games` (
  `game_id` VARCHAR(20) NOT NULL,
  `season` INT NOT NULL,
  `week` INT NOT NULL,
  `game_type` VARCHAR(10) NOT NULL,
  `home_team` VARCHAR(10) NOT NULL,
  `away_team` VARCHAR(10) NOT NULL,
  `home_score` INT NULL,
  `away_score` INT NULL,
  `total` INT NULL,
  `margin` INT NULL,
  `spread_line` DECIMAL(5,2) NULL,
  `total_line` DECIMAL(5,2) NULL,
  `home_rest` INT NULL,
  `away_rest` INT NULL,
  PRIMARY KEY (`game_id`),
  INDEX `idx_season_week` (`season`, `week`),
  INDEX `idx_home_team` (`home_team`),
  INDEX `idx_away_team` (`away_team`),
  CONSTRAINT `fk_games_home` FOREIGN KEY (`home_team`) REFERENCES `teams` (`team_abbr`),
  CONSTRAINT `fk_games_away` FOREIGN KEY (`away_team`) REFERENCES `teams` (`team_abbr`)
);

-- PLAYS: play-by-play (key columns for analytics)
CREATE TABLE `plays` (
  `play_id` BIGINT NOT NULL,
  `game_id` VARCHAR(20) NOT NULL,
  `season` INT NOT NULL,
  `week` INT NOT NULL,
  `posteam` VARCHAR(10) NULL,
  `defteam` VARCHAR(10) NULL,
  `down` INT NULL,
  `ydstogo` INT NULL,
  `yardline_100` INT NULL,
  `game_seconds_remaining` INT NULL,
  `score_differential` INT NULL,
  `posteam_score` INT NULL,
  `defteam_score` INT NULL,
  `yards_gained` INT NULL,
  `play_type` VARCHAR(30) NULL,
  PRIMARY KEY (`play_id`, `game_id`),
  INDEX `idx_plays_game` (`game_id`),
  INDEX `idx_plays_posteam` (`posteam`),
  INDEX `idx_plays_season` (`season`),
  CONSTRAINT `fk_plays_game` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`)
);

-- LINES: betting lines (open/close) by game
CREATE TABLE `lines` (
  `game_id` VARCHAR(20) NOT NULL,
  `line_type` VARCHAR(20) NOT NULL,
  `spread` DECIMAL(5,2) NULL,
  `total` DECIMAL(5,2) NULL,
  `source` VARCHAR(50) NULL,
  PRIMARY KEY (`game_id`, `line_type`),
  CONSTRAINT `fk_lines_game` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`)
);
