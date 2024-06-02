CREATE DATABASE IF NOT EXISTS moodofmusic;
USE moodofmusic;

CREATE TABLE IF NOT EXISTS accounts (
    accname VARCHAR(255) NOT NULL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS playlists (
    playlistID VARCHAR(100) NOT NULL,
    accname VARCHAR(255) NOT NULL,
    pldate DATE,
    prompt VARCHAR(10000),
    image_url VARCHAR(512),
    PRIMARY KEY (playlistID)
);
