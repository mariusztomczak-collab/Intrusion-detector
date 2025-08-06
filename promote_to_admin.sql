-- Promote the first user to admin role
-- Run this after you've registered your first user

-- Option 1: Promote by email (replace with your actual email)
-- SELECT promote_user_to_admin('your-email@example.com');

-- Option 2: Promote the first user in the system
UPDATE profiles SET role = 'admin' WHERE id = (SELECT id FROM profiles ORDER BY created_at ASC LIMIT 1);

-- Verify the change
SELECT username, role, created_at FROM profiles ORDER BY created_at; 