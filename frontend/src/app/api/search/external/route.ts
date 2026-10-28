import { NextResponse } from 'next/server';
import { queryArticles } from '@/lib/repository';
import { searchExternal } from '@/lib/externalSearch';

/**
 * GET /api/search/external?q= — news discovery beyond the local edition/database.
 * Runs on the server so provider keys (GNEWS_API_KEY) never reach the browser.
 * Results already present locally are removed.
 */
export async function GET(request: Request) {
    const url = new URL(request.url);
    const q = (url.searchParams.get('q') ?? '').trim().slice(0, 120);
    const since = (url.searchParams.get('since') ?? '').trim();
    if (!q) return NextResponse.json({ error: 'A search query is required.' }, { status: 400 });

    let local: { sourceUrl: string | null; title: string }[] = [];
    try {
        local = (await queryArticles({ q, limit: 100 })).articles;
    } catch {
        local = [];
    }
    const response = await searchExternal(q, local, since);
    return NextResponse.json(response, { status: response.status === 'unavailable' ? 502 : 200 });
}
