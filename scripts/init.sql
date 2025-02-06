CREATE TABLE IF NOT EXISTS session (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tiktok (
    id SERIAL PRIMARY KEY,
    title TEXT,
    channel TEXT,
    channel_id TEXT,
    channel_url TEXT,
    tiktok_url TEXT,
    thumbnail_url TEXT,
    timestamp INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    repost_count INTEGER,
    comment_count INTEGER,
    duration INTEGER,
    track TEXT,
    session_id TEXT REFERENCES session(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis (
    id SERIAL PRIMARY KEY,
    transcript TEXT NOT NULL,
    analysis TEXT NOT NULL,
    tags TEXT[],
    category TEXT NOT NULL,
    rating INTEGER NOT NULL,
    like BOOLEAN NOT NULL,
    tiktok_id INTEGER REFERENCES tiktok(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
