import { NextResponse } from 'next/server';
import { queryArticles } from '@/lib/repository';
import { parseArticleQuery } from '@/lib/query';

/**
 * GET /api/articles — paginated, filterable article list (handover §6 step 5).
 * Query: q, section (or legacy `category`), publisher, risk, verify=1, sort=newest|oldest, page, limit.
 */
export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    try {
        const result = await queryArticles(parseArticleQuery(searchParams));
        return NextResponse.json(result);
    } catch (err) {
        console.error('GET /api/articles failed:', err);
        return NextResponse.json({ error: 'Articles are temporarily unavailable.' }, { status: 503 });
    }
}
