import { afterEach, describe, expect, it, vi } from 'vitest';
import { normalise, parseQuery, rankArticles } from './search';
import { filterArticles } from './repository';
import type { Article } from './types';

function article(id: string, title: string, extra: Partial<Article> = {}): Article {
    return {
        id, title, publisher: 'BBC News', sourceUrl: `https://example.com/${id}`, imageUrl: null, excerpt: '', summary: null,
        summaryKind: null, section: 'world', author: null, publishedAt: '2026-10-27T10:00:00Z', ingestedAt: null, sentiment: null,
        credibility: { label: 'Low Risk', score: 0.1, confidence: null, needsVerification: false, reasoning: null },
        dimensions: null, groupId: null, eventTitle: null, origin: 'live-feed', analysisMethod: 'heuristic', ...extra,
    };
}

const pool = [
    article('1', 'Meta sued by states over teen mental health', { excerpt: 'A lawsuit filed on Monday accuses Facebook’s parent company of harm.' }),
    article('2', 'Gold prices hit record as metal demand surges'),
    article('3', 'Cyclone Arnab makes landfall in Andhra Pradesh', { section: 'india', publisher: 'The Hindu' }),
    article('4', 'Neil Young files second lawsuit against Trump'),
    article('5', 'Ballon d’Or in London – the most chaotic ever?', { section: 'sports', publishedAt: '2025-10-27T10:00:00Z' }),
];
const titles = (q: string, extra = {}) => filterArticles(pool, { q, ...extra }).articles.map(a => a.id);

describe('search parsing', () => {
    it('normalises case, accents and punctuation', () => {
        expect(normalise('  Ballon d’Or — “CHAOTIC”?! Café ')).toBe('ballon d or chaotic cafe');
    });

    it('treats years as a date hint and expands organisation aliases', () => {
        const p = parseQuery('Facebook lawsuit 2026');
        expect(p.years).toEqual([2026]);
        expect(p.terms).toEqual([['facebook', 'meta'], ['lawsuit']]);
    });
});

describe('local search', () => {
    it('finds an exact headline first', () => {
        expect(titles('Cyclone Arnab makes landfall in Andhra Pradesh')[0]).toBe('3');
    });

    it('matches partial headlines and word prefixes, case-insensitively', () => {
        expect(titles('ANDHRA landfal')).toEqual(['3']);
    });

    it('searches excerpts and publisher names, not only headlines', () => {
        expect(titles('lawsuit')).toEqual(expect.arrayContaining(['1', '4']));
        expect(titles('the hindu')).toEqual(['3']);
    });

    it('matches whole words: "meta" does not match "metal"', () => {
        expect(titles('meta')).toEqual(['1']);
    });

    it('lets a four-letter fragment find a longer word ("memo" → "memoir")', () => {
        expect(filterArticles([article('9', 'Sonia Gandhi says her memoir is bound to create tamasha')], { q: 'Sonia Gandhi memo' }).fullMatches).toBe(1);
    });

    it('finds "Facebook lawsuit 2026" through the Meta alias and the year', () => {
        const { articles, fullMatches } = filterArticles(pool, { q: 'Facebook lawsuit 2026' });
        expect(fullMatches).toBe(1);
        expect(articles[0].id).toBe('1');
    });

    it('excludes reports from other years when a year is given', () => {
        expect(titles('Ballon d’Or 2026')).toEqual([]);
        expect(titles('Ballon d’Or 2025')).toEqual(['5']);
    });

    it('returns labelled partial matches when no report has every term', () => {
        const { articles, fullMatches } = filterArticles(pool, { q: 'Trump lawsuit appeal' });
        expect(fullMatches).toBe(0);
        expect(articles.map(a => a.id)).toEqual(['4']);
    });

    it('returns nothing for a nonexistent topic', () => {
        expect(titles('zxqv quantum platypus')).toEqual([]);
    });

    it('combines the text query with section filters', () => {
        expect(titles('lawsuit', { section: 'india' })).toEqual([]);
        expect(titles('cyclone', { section: 'india' })).toEqual(['3']);
    });

    it('ranks headline matches above excerpt-only matches', () => {
        const ranked = rankArticles(pool, parseQuery('lawsuit'));
        expect(ranked[0].article.id).toBe('4');
    });
});

describe('external discovery', () => {
    afterEach(() => {
        vi.unstubAllGlobals();
        vi.unstubAllEnvs();
        vi.resetModules();
    });

    it('reports GDELT rate limiting as busy, with a configuration hint, not as an empty result', async () => {
        vi.stubEnv('GNEWS_API_KEY', '');
        vi.stubGlobal('fetch', vi.fn(async () => new Response('Please limit requests to one every 5 seconds', { status: 429 })));
        const { searchExternal } = await import('./externalSearch');
        const r = await searchExternal('Meta lawsuit', []);
        expect(r.status).toBe('rate-limited');
        expect(r.results).toEqual([]);
        expect(r.configHint).toContain('GNEWS_API_KEY');
    });

    it('keeps only GDELT headlines that contain every term and removes local duplicates', async () => {
        vi.stubEnv('GNEWS_API_KEY', '');
        const articles = [
            { url: 'https://a.com/1', title: 'Meta hit with privacy lawsuit in Texas', seendate: '20261020T101500Z', domain: 'a.com' },
            { url: 'https://b.com/2', title: 'Celebrity friends defend actor', seendate: '20261020T101500Z', domain: 'b.com' },
            { url: 'https://c.com/3', title: 'Facebook lawsuit settlement approved', seendate: '20261021T101500Z', domain: 'www.c.com' },
        ];
        const fetchMock = vi.fn<(url: string) => Promise<Response>>(async () => new Response(JSON.stringify({ articles }), { status: 200 }));
        vi.stubGlobal('fetch', fetchMock);
        const { searchExternal } = await import('./externalSearch');
        const r = await searchExternal('facebook lawsuit', [{ sourceUrl: 'https://c.com/3', title: 'x' }]);
        expect(r.status).toBe('ok');
        expect(r.results.map(x => x.title)).toEqual(['Meta hit with privacy lawsuit in Texas']);
        expect(r.results[0]).toMatchObject({ publisher: 'a.com', publishedAt: '2026-10-20T10:15:00Z', provider: 'GDELT', analysed: false });
        expect(new URL(String(fetchMock.mock.calls[0][0])).searchParams.get('query')).toBe('(facebook OR meta) lawsuit sourcelang:english');
    });

    it('uses GNews when a key is configured and analyses only reports with enough text', async () => {
        vi.stubEnv('GNEWS_API_KEY', 'test-key');
        const long = 'Meta Platforms was sued on Tuesday by a group of advertisers who say the company inflated audience figures, according to court filings reviewed by reporters.';
        const fetchMock = vi.fn<(url: string) => Promise<Response>>(async () => new Response(JSON.stringify({
            articles: [
                { title: 'Advertisers file lawsuit against Meta', description: long, content: 'More text ... [1200 chars]', url: 'https://n.com/a', publishedAt: '2026-10-21T08:00:00Z', source: { name: 'Example News' } },
                { title: 'Meta lawsuit dismissed', description: 'Short.', url: 'https://n.com/b', publishedAt: '2026-10-22T08:00:00Z', source: { name: 'Other' } },
            ],
        }), { status: 200 }));
        vi.stubGlobal('fetch', fetchMock);
        const { searchExternal, getExternalArticle } = await import('./externalSearch');
        const r = await searchExternal('Meta lawsuit', []);
        expect(r.provider).toBe('GNews');
        expect(r.results.map(x => [x.title, x.analysed]).sort()).toEqual([['Advertisers file lawsuit against Meta', true], ['Meta lawsuit dismissed', false]]);
        expect(String(fetchMock.mock.calls[0][0])).toContain('apikey=test-key');
        const full = r.results.find(x => x.analysed)!;
        const headlineOnly = r.results.find(x => !x.analysed)!;
        expect(getExternalArticle(full.id)?.origin).toBe('external');
        expect(getExternalArticle(full.id)?.credibility.confidence).toBeNull();
        expect(getExternalArticle(headlineOnly.id)).toBeNull();
    });
});
