import { NextResponse } from 'next/server';
import { getAnalytics } from '@/lib/repository';

/** GET /api/analytics — category, sentiment, risk, dimension and coverage statistics for the edition. */
export async function GET() {
    try {
        return NextResponse.json(await getAnalytics());
    } catch (err) {
        console.error('GET /api/analytics failed:', err);
        return NextResponse.json({ error: 'Analytics are temporarily unavailable.' }, { status: 503 });
    }
}
