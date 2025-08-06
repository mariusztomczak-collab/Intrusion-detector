-- Add INSERT policy for decisions table
CREATE POLICY "Users can insert their own decisions"
    ON decisions FOR INSERT
    TO authenticated
    WITH CHECK (
        user_id = (SELECT auth.uid())
    );

-- Add INSERT policy for service role (bypasses RLS)
CREATE POLICY "Service role can insert decisions"
    ON decisions FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Add UPDATE policy for decisions table
CREATE POLICY "Users can update their own decisions or all decisions if admin"
    ON decisions FOR UPDATE
    TO authenticated
    USING (
        user_id = (SELECT auth.uid()) OR
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- Add DELETE policy for decisions table
CREATE POLICY "Only admins can delete decisions"
    ON decisions FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    ); 