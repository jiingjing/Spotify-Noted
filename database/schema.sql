CREATE DATABASE spotify_db;
USE spotify_db;


-- Each ROW = one unique track 
-- track_id: SHA1 hash of normalised track|artist|album (stable across Spotify URI relinking and capitalisation differences)
-- in_library: TRUE if track is in user's saved library
CREATE TABLE tracks_metadata (
    track_id          CHAR(40) PRIMARY KEY,
    track_name        VARCHAR(255) NOT NULL,
    artist_name       VARCHAR(255) NOT NULL,
    album_name        VARCHAR(255),
    track_length_ms   INT,
    track_release_date DATE,
    track_language    VARCHAR(50),
    artist_country    VARCHAR(50),
    in_library        BOOLEAN NOT NULL
);

-- Maps Spotify URIs to track_id (one track_id can have multiple URIs due to Spotify relinking)
CREATE TABLE track_uris (
    spotify_track_uri VARCHAR(255) PRIMARY KEY,
    track_id          CHAR(40) NOT NULL,

    FOREIGN KEY (track_id) REFERENCES tracks_metadata(track_id)
);

-- Each ROW = one play event
CREATE TABLE listening_history (
    play_id    INT AUTO_INCREMENT PRIMARY KEY,
    track_id   CHAR(40) NOT NULL,
    time_stamp DATETIME NOT NULL,
    ms_played  INT NOT NULL,
    reason_start VARCHAR(50) NOT NULL,
    reason_end   VARCHAR(50) NOT NULL,
    shuffle    BOOLEAN NOT NULL,
    skipped    BOOLEAN NOT NULL,

    FOREIGN KEY (track_id) REFERENCES tracks_metadata(track_id)
);

-- Each ROW = one unique track (local file reference of .mp3 download)
CREATE TABLE tracks_audio (
    track_id        CHAR(40) PRIMARY KEY,
    audio_file_path VARCHAR(512),

    FOREIGN KEY (track_id) REFERENCES tracks_metadata(track_id)
);

-- Each ROW = one unique track (essentia features for audio analysis)
CREATE TABLE tracks_audio_features (
    track_id            CHAR(40) PRIMARY KEY,
    bpm                 FLOAT,
    musical_key         VARCHAR(10),
    scale               VARCHAR(10),
    top_genre_1         VARCHAR(100),
    top_genre_2         VARCHAR(100),
    top_genre_3         VARCHAR(100),
    mood_happy          FLOAT,
    mood_sad            FLOAT,
    mood_aggressive     FLOAT,
    mood_relaxed        FLOAT,
    mood_party          FLOAT,
    danceability        FLOAT,
    instrumentalness    FLOAT,
    valence             FLOAT,
    arousal             FLOAT,
    voice_gender_female FLOAT,
    voice_gender_male   FLOAT,
    mood_acoustic       FLOAT,
    mood_electronic     FLOAT,

    FOREIGN KEY (track_id) REFERENCES tracks_metadata(track_id)
);

-- Single ROW for display_name
CREATE TABLE display_name (
    name VARCHAR(255)
);