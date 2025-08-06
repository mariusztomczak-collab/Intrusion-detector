-- SQL script to add a new user to Supabase
-- Replace the values below with actual user data

-- Option 1: Add user directly to auth.users (if you have the password hash)
-- INSERT INTO auth.users (
--     id,
--     email,
--     encrypted_password,
--     email_confirmed_at,
--     created_at,
--     updated_at,
--     raw_app_meta_data,
--     raw_user_meta_data,
--     is_super_admin,
--     confirmation_token,
--     email_change,
--     email_change_token_new,
--     recovery_token
-- ) VALUES (
--     gen_random_uuid(),
--     'newuser@example.com',
--     crypt('password123', gen_salt('bf')),
--     now(),
--     now(),
--     now(),
--     '{"provider": "email", "providers": ["email"]}',
--     '{}',
--     false,
--     '',
--     '',
--     '',
--     ''
-- );

-- Option 2: Use the Supabase function (recommended)
-- This requires the user to be created through the auth system first
-- Then you can update their role

-- To promote an existing user to admin:
-- SELECT promote_user_to_admin('user@example.com');

-- To view all current users:
SELECT username, role, created_at FROM profiles ORDER BY created_at;

-- To add a test user (this will be created as 'user' role by default):
-- Just register through the web interface at http://localhost:7860 