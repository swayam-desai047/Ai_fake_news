import { NextResponse } from 'next/server';
import { getArticle } from '@/lib/repository';

/** GET /api/article/{id} — one article with its full dimension analysis and summary. */
export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    try {
        const found = await getArticle(decodeURIComponent(id));
        if (!found) return NextResponse.json({ error: 'Article not found in the current edition.' }, { status: 404 });
        return NextResponse.json({ article: found.article });
    } catch (err) {
        console.error('GET /api/article failed:', err);
        return NextResponse.json({ error: 'Article is temporarily unavailable.' }, { status: 503 });
    }
}
