-- schema.sql
-- 한국 음악 추천 데이터베이스 생성 스키마

-- 기존 테이블이 있다면 초기화를 위해 삭제합니다 (개발 단계용)
DROP TABLE IF EXISTS post_likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

-- 1. 사용자 테이블 (Users)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 음악 추천 게시글 테이블 (Posts)
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,          -- 곡명
    artist TEXT NOT NULL,         -- 아티스트명
    genre_tag TEXT,               -- 장르/무드 해시태그 (예: #댄스팝, #드라이브)
    youtube_url TEXT,             -- 유튜브 링크 등
    content TEXT NOT NULL,        -- 추천 이유 및 덧붙일 말
    likes_count INTEGER DEFAULT 0,-- 좋아요 수 카운트
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. 댓글 테이블 (Comments)
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,     -- 어떤 글에 달린 댓글인지
    user_id INTEGER NOT NULL,     -- 누가 달았는지
    body TEXT NOT NULL,           -- 댓글 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 4. 조아요 중복 방지 테이블 (Post Likes)
CREATE TABLE post_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);
