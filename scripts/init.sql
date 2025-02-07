CREATE TABLE IF NOT EXISTS session (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'failed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tiktok (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    channel TEXT,
    channel_id TEXT,
    channel_url TEXT,
    tiktok_url TEXT UNIQUE,
    thumbnail_url TEXT,
    timestamp INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    repost_count INTEGER,
    comment_count INTEGER,
    duration INTEGER,
    track TEXT,
    session_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) 
        REFERENCES session(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript TEXT NOT NULL,
    analysis TEXT NOT NULL,
    tags TEXT NOT NULL,
    category TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 10),
    like BOOLEAN NOT NULL,
    tiktok_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tiktok_id) 
        REFERENCES tiktok(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT one_analysis_per_tiktok UNIQUE (tiktok_id)
);
