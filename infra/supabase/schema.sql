-- Supabase schema from specifications.md

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE la_so (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  birth_date DATE NOT NULL,
  birth_time TEXT NOT NULL,
  gender TEXT NOT NULL,
  chart_system TEXT NOT NULL CHECK (chart_system IN ('TUVI', 'BATU', 'TUVI_BATU')),
  chart_data JSONB NOT NULL,
  chart_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  la_so_id UUID NOT NULL UNIQUE REFERENCES la_so(id) ON DELETE CASCADE,
  title TEXT,
  summary TEXT,
  messages JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE source_chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_url TEXT,
  domain TEXT NOT NULL,
  source_page INT,
  title TEXT,
  chunk_text TEXT NOT NULL,
  chunk_hash TEXT UNIQUE NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_update_timestamp
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER la_so_update_timestamp
BEFORE UPDATE ON la_so
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER chat_sessions_update_timestamp
BEFORE UPDATE ON chat_sessions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_la_so_user_id ON la_so(user_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_source_chunks_hash ON source_chunks(chunk_hash);
CREATE INDEX idx_source_chunks_domain ON source_chunks(domain);
