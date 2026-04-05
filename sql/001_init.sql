-- Discord Todo 챗봇 — 초기 스키마 (Supabase / Postgres)
-- rooms: Discord 채널(또는 스레드) 단위
-- todos: 할 일 (room 1:N)

CREATE TABLE IF NOT EXISTS rooms (
    id              BIGSERIAL PRIMARY KEY,
    discord_room_id TEXT        NOT NULL,
    guild_id        TEXT        NOT NULL,
    room_name       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rooms_discord_room UNIQUE (discord_room_id)
);

CREATE INDEX IF NOT EXISTS idx_rooms_guild_id ON rooms (guild_id);

CREATE TABLE IF NOT EXISTS todos (
    id              BIGSERIAL PRIMARY KEY,
    room_id         BIGINT      NOT NULL REFERENCES rooms (id) ON DELETE CASCADE,
    discord_user_id TEXT        NOT NULL,
    task_text       TEXT        NOT NULL,
    done            BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_todos_room_id ON todos (room_id);
CREATE INDEX IF NOT EXISTS idx_todos_room_user ON todos (room_id, discord_user_id);
CREATE INDEX IF NOT EXISTS idx_todos_done ON todos (room_id, done);

-- updated_at 자동 갱신 (Supabase에서 plpgsql 사용 가능한 경우)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_todos_updated_at ON todos;
CREATE TRIGGER trg_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();
