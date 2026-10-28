import { createClient } from '@supabase/supabase-js';

const rawUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const rawKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(
    rawUrl &&
    rawKey &&
    (rawUrl.startsWith('http://') || rawUrl.startsWith('https://')) &&
    !rawUrl.toLowerCase().includes('placeholder') &&
    !rawUrl.toLowerCase().includes('your_supabase_project_url') &&
    !rawUrl.toLowerCase().includes('your_project_url')
);

const supabaseUrl = isSupabaseConfigured ? rawUrl! : 'https://placeholder.supabase.co';
const supabaseAnonKey = isSupabaseConfigured ? rawKey! : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.placeholder';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
