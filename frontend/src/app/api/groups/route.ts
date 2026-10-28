import { NextResponse } from 'next/server';
import { getGroups } from '@/lib/repository';

/** GET /api/groups — cross-source event clusters with their member articles. */
export async function GET() {
    try {
        return NextResponse.json(await getGroups());
    } catch (err) {
        console.error('GET /api/groups failed:', err);
        return NextResponse.json({ error: 'Coverage groups are temporarily unavailable.' }, { status: 503 });
    }
}
