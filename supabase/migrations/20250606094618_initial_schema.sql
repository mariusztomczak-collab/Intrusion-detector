-- Create profiles table that extends auth.users
CREATE TABLE profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create decisions table
CREATE TABLE decisions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    correlation_id TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('single', 'batch')),
    batch_filename TEXT,
    batch_file_contents TEXT,
    model_version TEXT,
    classification_result TEXT NOT NULL CHECK (classification_result IN ('NORMAL', 'MALICIOUS')),
    
    -- Model features
    logged_in BOOLEAN NOT NULL,
    count INTEGER NOT NULL,
    serror_rate DOUBLE PRECISION NOT NULL,
    srv_serror_rate DOUBLE PRECISION NOT NULL,
    same_srv_rate DOUBLE PRECISION NOT NULL,
    dst_host_srv_count INTEGER NOT NULL,
    dst_host_same_srv_rate DOUBLE PRECISION NOT NULL,
    dst_host_serror_rate DOUBLE PRECISION NOT NULL,
    dst_host_srv_serror_rate DOUBLE PRECISION NOT NULL,
    flag VARCHAR(10) NOT NULL
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX idx_profiles_username ON profiles (username);
CREATE INDEX idx_decisions_timestamp ON decisions (timestamp);
CREATE INDEX idx_decisions_correlation_id ON decisions (correlation_id);
CREATE INDEX idx_decisions_classification_result ON decisions (classification_result);
CREATE INDEX idx_decisions_model_version ON decisions (model_version);
CREATE INDEX idx_decisions_source_type ON decisions (source_type);
CREATE INDEX idx_decisions_flag ON decisions (flag);
CREATE INDEX idx_decisions_user_id ON decisions (user_id);

-- Create RLS Policies for profiles
CREATE POLICY "Users can view their own profile or all profiles if admin"
    ON profiles FOR SELECT
    TO authenticated
    USING (
        id = (SELECT auth.uid()) OR
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

CREATE POLICY "Only admins can update profiles"
    ON profiles FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- Create RLS Policies for decisions
CREATE POLICY "Users can view their own decisions or all decisions if admin"
    ON decisions FOR SELECT
    TO authenticated
    USING (
        user_id = (SELECT auth.uid()) OR
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- Create function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = ''
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.profiles (id, username, role)
    VALUES (new.id, new.email, 'admin');
    RETURN new;
END;
$$;

-- Create trigger for new user creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user(); 