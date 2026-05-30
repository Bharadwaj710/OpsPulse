-- SECTION A: Execution SQL (Schema & RLS)

-- 1. Extend Tasks Table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS product_image_url TEXT;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS revision_note TEXT;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP;

-- 2. Extend Activity Logs Table (acts as Audit Log)
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS entity_type VARCHAR(50) DEFAULT 'task';
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS old_value JSONB;
ALTER TABLE activity_logs ADD COLUMN IF NOT EXISTS new_value JSONB;

-- 3. Create Generated Images Table
CREATE TABLE IF NOT EXISTS generated_images (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    generated_by UUID REFERENCES users(id),
    image_type VARCHAR(50) NOT NULL,
    angle VARCHAR(20),
    image_url TEXT NOT NULL,
    prompt_used TEXT,
    metadata JSONB,
    is_final BOOLEAN DEFAULT false,
    job_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Create Generation Jobs Table
CREATE TABLE IF NOT EXISTS generation_jobs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 5. Safe RLS Policy Implementation (No Recursion)

-- First, create a SECURITY DEFINER function to check if a user is an admin
-- This bypasses RLS internally, preventing the infinite recursion of checking the users table
CREATE OR REPLACE FUNCTION public.is_admin(user_id uuid)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM users
    WHERE id = user_id AND role = 'admin'
  );
$$;

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Admins have full access to everything (Using the safe function)
CREATE POLICY "Admins have full access users" ON users FOR ALL USING (public.is_admin(auth.uid()));
CREATE POLICY "Admins have full access tasks" ON tasks FOR ALL USING (public.is_admin(auth.uid()));
CREATE POLICY "Admins have full access logs" ON activity_logs FOR ALL USING (public.is_admin(auth.uid()));
CREATE POLICY "Admins have full access images" ON generated_images FOR ALL USING (public.is_admin(auth.uid()));
CREATE POLICY "Admins have full access jobs" ON generation_jobs FOR ALL USING (public.is_admin(auth.uid()));

-- Policy: Users can view their assigned/created tasks and related data
CREATE POLICY "Users view assigned tasks" ON tasks FOR SELECT USING (assigned_to = auth.uid() OR created_by = auth.uid());
CREATE POLICY "Users view their logs" ON activity_logs FOR SELECT USING (performed_by = auth.uid() OR task_id IN (SELECT id FROM tasks WHERE assigned_to = auth.uid() OR created_by = auth.uid()));
CREATE POLICY "Users view their generated images" ON generated_images FOR SELECT USING (generated_by = auth.uid() OR task_id IN (SELECT id FROM tasks WHERE assigned_to = auth.uid()));
CREATE POLICY "Users view their generation jobs" ON generation_jobs FOR SELECT USING (task_id IN (SELECT id FROM tasks WHERE assigned_to = auth.uid()));

-- ==============================================================================

-- SECTION B: Verification SQL (Run this to verify success)

/*
-- Verify table structures
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tasks';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'activity_logs';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'generated_images';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'generation_jobs';

-- Verify RLS is enabled
SELECT relname, relrowsecurity FROM pg_class WHERE relname IN ('users', 'tasks', 'activity_logs', 'generated_images', 'generation_jobs');

-- Verify policies exist
SELECT tablename, policyname FROM pg_policies WHERE tablename IN ('users', 'tasks', 'activity_logs', 'generated_images', 'generation_jobs');
*/

-- ==============================================================================

-- SECTION C: Rollback SQL (Run this if you need to undo)

/*
-- Drop policies
DROP POLICY IF EXISTS "Admins have full access users" ON users;
DROP POLICY IF EXISTS "Admins have full access tasks" ON tasks;
DROP POLICY IF EXISTS "Admins have full access logs" ON activity_logs;
DROP POLICY IF EXISTS "Admins have full access images" ON generated_images;
DROP POLICY IF EXISTS "Admins have full access jobs" ON generation_jobs;
DROP POLICY IF EXISTS "Users view assigned tasks" ON tasks;
DROP POLICY IF EXISTS "Users view their logs" ON activity_logs;
DROP POLICY IF EXISTS "Users view their generated images" ON generated_images;
DROP POLICY IF EXISTS "Users view their generation jobs" ON generation_jobs;

-- Drop function
DROP FUNCTION IF EXISTS public.is_admin(uuid);

-- Disable RLS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE generated_images DISABLE ROW LEVEL SECURITY;
ALTER TABLE generation_jobs DISABLE ROW LEVEL SECURITY;

-- Drop tables
DROP TABLE IF EXISTS generated_images CASCADE;
DROP TABLE IF EXISTS generation_jobs CASCADE;

-- Remove columns
ALTER TABLE tasks DROP COLUMN IF EXISTS product_image_url;
ALTER TABLE tasks DROP COLUMN IF EXISTS submitted_at;
ALTER TABLE tasks DROP COLUMN IF EXISTS accepted_at;
ALTER TABLE tasks DROP COLUMN IF EXISTS revision_note;
ALTER TABLE tasks DROP COLUMN IF EXISTS assigned_at;

ALTER TABLE activity_logs DROP COLUMN IF EXISTS entity_type;
ALTER TABLE activity_logs DROP COLUMN IF EXISTS old_value;
ALTER TABLE activity_logs DROP COLUMN IF EXISTS new_value;
*/
