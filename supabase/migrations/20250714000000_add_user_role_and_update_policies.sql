-- Migration: Add user role and update policies for read-only decisions
-- Date: 2025-07-14

-- 1. Update the role constraint to include 'user' role
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_role_check;
ALTER TABLE profiles ADD CONSTRAINT profiles_role_check CHECK (role IN ('admin', 'user'));

-- 2. Update the trigger function to assign 'user' role by default instead of 'admin'
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = ''
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.profiles (id, username, role)
    VALUES (new.id, new.email, 'user');  -- Changed from 'admin' to 'user'
    RETURN new;
END;
$$;

-- 3. Drop existing policies for decisions table
DROP POLICY IF EXISTS "Users can view their own decisions or all decisions if admin" ON decisions;
DROP POLICY IF EXISTS "Users can update their own decisions or all decisions if admin" ON decisions;
DROP POLICY IF EXISTS "Only admins can delete decisions" ON decisions;

-- 4. Create new read-only policies for decisions table
-- Users can view their own decisions
CREATE POLICY "Users can view their own decisions"
    ON decisions FOR SELECT
    TO authenticated
    USING (user_id = (SELECT auth.uid()));

-- Admins can view all decisions
CREATE POLICY "Admins can view all decisions"
    ON decisions FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- 5. Keep the INSERT policies (users can still create decisions)
-- These policies are already correct and don't need changes

-- 6. Remove UPDATE and DELETE policies - decisions are now read-only
-- No UPDATE or DELETE policies will be created, making decisions read-only

-- 7. Update profiles policies to be more restrictive
DROP POLICY IF EXISTS "Users can view their own profile or all profiles if admin" ON profiles;
DROP POLICY IF EXISTS "Only admins can update profiles" ON profiles;

-- Users can only view their own profile
CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    TO authenticated
    USING (id = (SELECT auth.uid()));

-- Admins can view all profiles
CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- Only admins can update profiles
CREATE POLICY "Only admins can update profiles"
    ON profiles FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- 8. Create a function to promote a user to admin (for initial setup)
CREATE OR REPLACE FUNCTION promote_user_to_admin(user_email TEXT)
RETURNS VOID
SECURITY DEFINER
SET search_path = ''
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE profiles 
    SET role = 'admin' 
    WHERE username = user_email;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User with email % not found', user_email;
    END IF;
END;
$$;

-- 9. Create a function to demote an admin to user
CREATE OR REPLACE FUNCTION demote_admin_to_user(user_email TEXT)
RETURNS VOID
SECURITY DEFINER
SET search_path = ''
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE profiles 
    SET role = 'user' 
    WHERE username = user_email AND role = 'admin';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Admin with email % not found', user_email;
    END IF;
END;
$$; 