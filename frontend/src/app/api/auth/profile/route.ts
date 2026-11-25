import { NextRequest, NextResponse } from 'next/server';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

/**
 * POST /api/auth/profile
 * Simple name-based auth. Checks if the given name already exists
 * in the `named_visitors` table. If not, inserts it.
 * Falls back gracefully when Supabase credentials are not yet configured.
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { name } = body;

        if (!name || typeof name !== 'string' || name.trim().length === 0) {
            return NextResponse.json({ error: 'Name is required' }, { status: 400 });
        }

        const cleanName = name.trim();
        // Same limit as the named_visitors_name_length constraint in the database.
        if (cleanName.length > 40) {
            return NextResponse.json({ error: 'Name must be 40 characters or fewer' }, { status: 400 });
        }

        if (!isSupabaseConfigured) {
            // Local fallback session
            return NextResponse.json({
                success: true,
                user: {
                    id: "local-demo-user",
                    name: cleanName,
                    created_at: new Date().toISOString()
                },
                isNew: false
            });
        }

        // Check if visitor already exists in Supabase
        const { data: existingUser, error: checkError } = await supabase
            .from('named_visitors')
            .select('id, name, created_at')
            .eq('name', cleanName)
            .maybeSingle();

        if (checkError) {
            console.warn('DB check error, falling back to local session:', checkError.message);
            return NextResponse.json({
                success: true,
                user: {
                    id: "fallback-visitor-id",
                    name: cleanName,
                    created_at: new Date().toISOString()
                },
                isNew: false
            });
        }

        if (existingUser) {
            return NextResponse.json({ success: true, user: existingUser, isNew: false });
        }

        // New visitor — insert
        const { data: newUser, error: insertError } = await supabase
            .from('named_visitors')
            .insert({ name: cleanName })
            .select()
            .single();

        if (insertError) {
            console.warn('DB insert error, falling back to local session:', insertError.message);
            return NextResponse.json({
                success: true,
                user: {
                    id: "fallback-visitor-id",
                    name: cleanName,
                    created_at: new Date().toISOString()
                },
                isNew: true
            });
        }

        return NextResponse.json({ success: true, user: newUser, isNew: true });
    } catch (err) {
        console.error('Auth profile route error:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
