-- Supabase seed data for local development and test purposes.
-- Note: auth.users is managed by Supabase Auth, so we create profile + la_so + chat_sessions with placeholder IDs.

INSERT INTO profiles (id, display_name, avatar_url)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Test User',
  NULL
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO la_so (id, user_id, label, birth_date, birth_time, gender, chart_system, chart_data, chart_version)
VALUES (
  '00000000-0000-0000-0000-000000000010',
  '00000000-0000-0000-0000-000000000001',
  'Chart 1',
  '1990-01-01',
  '08:00',
  'MALE',
  'TUVI',
  '{"source":"seed","description":"Sample chart data"}',
  'v1'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO chat_sessions (id, user_id, la_so_id, title, summary, messages)
VALUES (
  '00000000-0000-0000-0000-000000000020',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000010',
  'Sample chat',
  'Seed chat session for local development.',
  '[]'::jsonb
)
ON CONFLICT (id) DO NOTHING;
