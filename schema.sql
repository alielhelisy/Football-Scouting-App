-- Run this in SSMS after creating the ScoutingApp database
-- Or it is run automatically when you start the Flask app

IF OBJECT_ID('reports', 'U') IS NOT NULL DROP TABLE reports;
IF OBJECT_ID('players', 'U') IS NOT NULL DROP TABLE players;
IF OBJECT_ID('users',   'U') IS NOT NULL DROP TABLE users;

CREATE TABLE users (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    username      NVARCHAR(100) UNIQUE NOT NULL,
    name          NVARCHAR(100) NULL,
    surname       NVARCHAR(100) NULL,
    email         NVARCHAR(255) NULL,
    password_hash NVARCHAR(64)  NOT NULL,
    role          NVARCHAR(10)  NOT NULL DEFAULT 'SCOUT'
);

CREATE TABLE players (
    id       INT IDENTITY(1,1) PRIMARY KEY,
    user_id  INT           NOT NULL,
    name     NVARCHAR(100) NOT NULL,
    team     NVARCHAR(100) NOT NULL DEFAULT '',
    position NVARCHAR(20)  NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE reports (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    player_id      INT           NOT NULL,
    rating         DECIMAL(2,1) NOT NULL CHECK(rating BETWEEN 1 AND 5 AND rating * 2 = FLOOR(rating * 2)),
    minutes_played INT           NOT NULL DEFAULT 0,
    goals_scored   INT           NOT NULL DEFAULT 0,
    received_cards NVARCHAR(10)  NOT NULL DEFAULT 'None',
    rated_position NVARCHAR(20)  NOT NULL,
    comments       NVARCHAR(MAX),
    created_at     DATETIME      NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);
