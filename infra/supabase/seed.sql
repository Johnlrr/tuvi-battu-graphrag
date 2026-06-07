-- Supabase seed data for local development and test purposes.
-- Replace values with valid Supabase auth user IDs and secret keys if needed.

INSERT INTO auth.users (id, email, email_confirmed_at, app_metadata, user_metadata, created_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'test@example.com',
  NOW(),
  '{}'::jsonb,
  '{}'::jsonb,
  NOW()
)
ON CONFLICT (id) DO NOTHING;

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
