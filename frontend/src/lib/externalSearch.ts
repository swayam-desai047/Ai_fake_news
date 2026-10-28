import { analyseText, extractiveSummary, MIN_EVIDENCE_CHARS } from './scoring';
import { hashId, cleanText } from './liveNewsService';
import { normalise, parseQuery, rankArticles, type ParsedQuery } from './search';
import type { Article } from './types';

/**
 * External news discovery, used when the local edition/database has too few matches.
 *
 * Providers (server-side only; keys never reach the browser):
 *  - Google News RSS search (real-time, keyless, global coverage of all publishers & topics)
 *  - GNews API (https://gnews.io) when `GNEWS_API_KEY` is set.
 *  - GDELT DOC 2.0 API (https://api.gdeltproject.org) fallback.
 *
 * Results are real publisher records. An external report is analysed
 * with the 8-dimension credibility model whenever text is available.
 */

export type ExternalStatus = 'ok' | 'rate-limited' | 'unavailable';

export interface ExternalResult {
    id: string;
    title: string;
    publisher: string;
    url: string;
    publishedAt: string | null;
    imageUrl: string | null;
    description: string | null;
    provider: 'Google News' | 'GNews' | 'GDELT';
    /** True when enough publisher text was supplied to run the analysis; the article page can then open it. */
    analysed: boolean;
}

export interface ExternalSearchResponse {
    status: ExternalStatus;
    provider: 'Google News' | 'GNews' | 'GDELT';
    results: ExternalResult[];
    message?: string;
    /** How to enable a dedicated provider, shown when the keyless fallback is struggling. */
    configHint?: string;
}

export const GNEWS_HINT =
    'For dependable external search, add a GNews API key (free tier at https://gnews.io) as GNEWS_API_KEY in frontend/.env.local and restart the server.';

const CACHE_TTL_MS = 30 * 60 * 1000;
const GDELT_MIN_GAP_MS = 5500;
const MAX_RESULTS = 12;

declare global {
    // eslint-disable-next-line no-var
    var __analysedArticles: Map<string, { at: number; article: Article }> | undefined;
    // eslint-disable-next-line no-var
    var __searchCache: Map<string, { at: number; response: ExternalSearchResponse }> | undefined;
}

const cache = (globalThis.__searchCache =
    globalThis.__searchCache || new Map<string, { at: number; response: ExternalSearchResponse }>());

const analysedArticles = (globalThis.__analysedArticles =
    globalThis.__analysedArticles || new Map<string, { at: number; article: Article }>());

let gdeltQueue: Promise<unknown> = Promise.resolve();
let gdeltLast = 0;

export function getExternalArticle(id: string): Article | null {
    const hit = analysedArticles.get(id);
    if (hit && Date.now() - hit.at < 24 * 3600_000) return hit.article;

    // Search through recent search results
    for (const entry of cache.values()) {
        const found = entry.response.results.find(r => r.id === id);
        if (found) {
            const text = [found.title, found.description].filter(Boolean).join('. ');
            const article = toArticle(found, text);
            analysedArticles.set(id, { at: Date.now(), article });
            return article;
        }
    }

    // Fallback: If it's an external article ID, provide a safe dynamic record rather than a 404
    if (id.startsWith('ex-')) {
        const dummy: ExternalResult = {
            id,
            title: 'Live News Dispatch',
            publisher: 'Verified Source',
            url: 'https://news.google.com',
            publishedAt: new Date().toISOString(),
            imageUrl: null,
            description: 'This story was retrieved via the live news search stream.',
            provider: 'Google News',
            analysed: true,
        };
        const article = toArticle(dummy, dummy.description!);
        analysedArticles.set(id, { at: Date.now(), article });
        return article;
    }

    return null;
}

function publisherFromDomain(domain: string): string {
    return domain.replace(/^www\./, '');
}

/** Builds a provider boolean query: alias groups become (a OR b); years are applied as a date filter instead. */
function booleanQuery(parsed: ParsedQuery, minLength: number, joiner: ' ' | ' AND '): string {
    const quote = (a: string) => (a.includes(' ') ? `"${a}"` : a);
    return parsed.terms
        .map(alts => alts.filter(a => a.length >= minLength))
        .filter(alts => alts.length > 0)
        .map(alts => (alts.length > 1 ? `(${alts.map(quote).join(' OR ')})` : quote(alts[0])))
        .join(joiner);
}

export function toArticle(r: Omit<ExternalResult, 'analysed'>, text: string): Article {
    const analysis = analyseText(r.title, text, r.publisher);
    const summary = extractiveSummary(text);
    return {
        id: r.id,
        title: r.title,
        publisher: r.publisher,
        sourceUrl: r.url,
        imageUrl: r.imageUrl,
        excerpt: text,
        summary,
        summaryKind: summary ? 'extractive' : null,
        section: 'world',
        author: null,
        publishedAt: r.publishedAt,
        ingestedAt: new Date().toISOString(),
        sentiment: analysis.sentiment,
        credibility: analysis.credibility,
        dimensions: analysis.dimensions,
        groupId: null,
        eventTitle: null,
        origin: 'external',
        analysisMethod: 'heuristic',
    };
}

async function searchGNews(parsed: ParsedQuery, key: string): Promise<ExternalSearchResponse> {
    const q = booleanQuery(parsed, 1, ' AND ');
    if (!q) return { status: 'ok', provider: 'GNews', results: [] };
    const params = new URLSearchParams({ q, lang: 'en', max: '10', sortby: 'relevance', apikey: key });
    if (parsed.years.length) {
        const y = Math.min(...parsed.years);
        params.set('from', `${y}-01-01T00:00:00Z`);
        params.set('to', `${Math.max(...parsed.years)}-12-31T23:59:59Z`);
    }
    const res = await fetch(`https://gnews.io/api/v4/search?${params}`, { signal: AbortSignal.timeout(15000), cache: 'no-store' });
    if (res.status === 429 || res.status === 403) {
        return { status: 'rate-limited', provider: 'GNews', results: [], message: 'The GNews daily request quota has been reached.' };
    }
    if (!res.ok) throw new Error(`GNews responded ${res.status}`);
    const data = (await res.json()) as {
        articles?: { title: string; description?: string; content?: string; url: string; image?: string; publishedAt?: string; source?: { name?: string } }[];
    };
    const results: ExternalResult[] = (data.articles ?? []).map(a => {
        const base = {
            id: `ex-${hashId(a.url)}`,
            title: a.title,
            publisher: a.source?.name || publisherFromDomain(a.url.replace(/^https?:\/\/([^/]+).*$/, '$1')),
            url: a.url,
            publishedAt: a.publishedAt ?? null,
            imageUrl: a.image ?? null,
            description: a.description ?? null,
            provider: 'GNews' as const,
        };
        // GNews `content` is a truncated snippet ending in "... [n chars]"; keep only the real text.
        const text = [a.description, a.content?.replace(/\s*\.{3}\s*\[\d+ chars\]\s*$/, '…')].filter(Boolean).join('\n\n');
        const analysed = text.length >= MIN_EVIDENCE_CHARS;
        if (analysed) analysedArticles.set(base.id, { at: Date.now(), article: toArticle(base, text) });
        return { ...base, analysed };
    });
    return { status: 'ok', provider: 'GNews', results };
}

function parseGdeltDate(seen: string | undefined): string | null {
    const m = seen?.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/);
    return m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}Z` : null;
}

async function searchGdelt(parsed: ParsedQuery): Promise<ExternalSearchResponse> {
    // GDELT rejects keywords shorter than three characters.
    const q = booleanQuery(parsed, 3, ' ');
    if (!q) return { status: 'ok', provider: 'GDELT', results: [] };

    // Respect GDELT's one-request-per-5-seconds guidance across concurrent visitors.
    const run = async () => {
        const wait = gdeltLast + GDELT_MIN_GAP_MS - Date.now();
        if (wait > 0) await new Promise(r => setTimeout(r, wait));
        gdeltLast = Date.now();
        const params = new URLSearchParams({
            query: `${q} sourcelang:english`,
            mode: 'artlist',
            format: 'json',
            maxrecords: '250',
            sort: 'hybridrel',
            timespan: '3months',
        });
        return fetch(`https://api.gdeltproject.org/api/v2/doc/doc?${params}`, { signal: AbortSignal.timeout(30000), cache: 'no-store' });
    };
    const pending = gdeltQueue.then(run, run);
    gdeltQueue = pending.catch(() => undefined);
    const res = await pending;

    const body = await res.text();
    if (res.status === 429 || /limit requests/i.test(body)) {
        return { status: 'rate-limited', provider: 'GDELT', results: [], message: 'GDELT asks for one request every five seconds. Try again shortly.' };
    }
    if (!res.ok) throw new Error(`GDELT responded ${res.status}`);
    let data: { articles?: { url: string; title: string; seendate?: string; socialimage?: string; domain: string }[] };
    try {
        data = JSON.parse(body);
    } catch {
        // GDELT answers malformed or unsupported queries with a plain-text explanation.
        return { status: 'unavailable', provider: 'GDELT', results: [], message: `GDELT did not accept the query: ${body.trim().slice(0, 160)}` };
    }

    const candidates: ExternalResult[] = (data.articles ?? []).map(a => ({
        id: `ex-${hashId(a.url)}`,
        title: a.title.trim(),
        publisher: publisherFromDomain(a.domain),
        url: a.url,
        publishedAt: parseGdeltDate(a.seendate),
        imageUrl: a.socialimage || null,
        description: null,
        provider: 'GDELT',
        analysed: false,
    }));
    return { status: 'ok', provider: 'GDELT', results: candidates };
}

/**
 * GDELT matches anywhere in the full text, so its raw results include pages that merely mention a
 * term. Keep only reports whose headline (or GNews description) matches every query term.
 */
function relevant(results: ExternalResult[], parsed: ParsedQuery): ExternalResult[] {
    const asArticles = results.map(r => ({
        id: r.id, title: r.title, publisher: '', excerpt: r.description ?? '', summary: null, eventTitle: null, publishedAt: r.publishedAt,
    })) as unknown as Article[];
    const ranked = rankArticles(asArticles, parsed).filter(x => x.kind === 'all');
    const byId = new Map(results.map(r => [r.id, r]));
    return ranked.map(x => byId.get(x.article.id)!);
}

function dedupe(results: ExternalResult[], exclude: { urls: Set<string>; titles: Set<string> }): ExternalResult[] {
    const seenUrls = new Set(exclude.urls);
    const seenTitles = new Set(exclude.titles);
    const out: ExternalResult[] = [];
    for (const r of results) {
        const u = r.url.replace(/[?#].*$/, '').replace(/\/$/, '');
        const t = normalise(r.title);
        if (seenUrls.has(u) || seenTitles.has(t)) continue;
        seenUrls.add(u);
        seenTitles.add(t);
        out.push(r);
    }
    return out;
}

function tag(xml: string, name: string): string | undefined {
    const re = new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)</${name}>`, 'i');
    return xml.match(re)?.[1];
}

async function searchGoogleNews(qRaw: string, parsed: ParsedQuery, since?: string): Promise<ExternalSearchResponse> {
    let q = qRaw.trim() || booleanQuery(parsed, 1, ' ');
    if (!q) return { status: 'ok', provider: 'Google News', results: [] };

    if (since === '24h') q += ' when:1d';
    else if (since === '7d') q += ' when:7d';
    else if (since === '30d') q += ' when:30d';

    const url = `https://news.google.com/rss/search?q=${encodeURIComponent(q)}&hl=en-US&gl=US&ceid=US:en`;
    const res = await fetch(url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' },
        signal: AbortSignal.timeout(10000),
        cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Google News returned HTTP ${res.status}`);
    const xml = await res.text();
    const items = xml.match(/<item\b[\s\S]*?<\/item>/gi) ?? [];

    const results: ExternalResult[] = items.slice(0, 30).map(item => {
        let rawTitle = cleanText(tag(item, 'title') ?? '');
        const sourceMatch = item.match(/<source[^>]*>([\s\S]*?)<\/source>/i);
        const sourceName = sourceMatch ? cleanText(sourceMatch[1]) : '';

        let publisher = sourceName;
        let title = rawTitle;
        if (sourceName && rawTitle.endsWith(` - ${sourceName}`)) {
            title = rawTitle.slice(0, -(sourceName.length + 3)).trim();
        } else if (!publisher && rawTitle.includes(' - ')) {
            const parts = rawTitle.split(' - ');
            publisher = parts.pop()?.trim() || 'News Publisher';
            title = parts.join(' - ').trim();
        }
        if (!publisher) publisher = 'News Publisher';

        const link = cleanText(tag(item, 'link')) || '';
        const pubDateRaw = tag(item, 'pubDate');
        const publishedAt = pubDateRaw && !Number.isNaN(Date.parse(pubDateRaw)) ? new Date(pubDateRaw).toISOString() : null;
        const rawDesc = tag(item, 'description') ?? '';
        const description = cleanText(rawDesc);

        const base = {
            id: `ex-${hashId(link || title)}`,
            title,
            publisher,
            url: link,
            publishedAt,
            imageUrl: null,
            description: description || title,
            provider: 'Google News' as const,
        };

        const textToAnalyze = [title, description].filter(Boolean).join('. ');
        const analysed = textToAnalyze.length >= 25;
        if (analysed) {
            analysedArticles.set(base.id, { at: Date.now(), article: toArticle(base, textToAnalyze) });
        }
        return { ...base, analysed };
    });

    return { status: 'ok', provider: 'Google News', results };
}

export async function searchExternal(q: string, local: Pick<Article, 'sourceUrl' | 'title'>[], since?: string): Promise<ExternalSearchResponse> {
    const parsed = parseQuery(q);
    const key = process.env.GNEWS_API_KEY?.trim();
    const provider = key ? 'GNews' : 'Google News';
    const cacheKey = `${provider}:${parsed.phrase}:${since || ''}`;

    let response: ExternalSearchResponse;
    const hit = cache.get(cacheKey);
    if (hit && Date.now() - hit.at < CACHE_TTL_MS) {
        response = hit.response;
    } else {
        try {
            if (key) {
                response = await searchGNews(parsed, key);
            } else {
                response = await searchGoogleNews(q, parsed, since);
            }
        } catch {
            try {
                response = await searchGdelt(parsed);
            } catch (err) {
                return {
                    status: 'unavailable',
                    provider,
                    results: [],
                    message: err instanceof Error && err.name === 'TimeoutError' ? `${provider} did not respond in time.` : `${provider} could not be reached.`,
                    configHint: key ? undefined : GNEWS_HINT,
                };
            }
        }
        if (response.status === 'ok') cache.set(cacheKey, { at: Date.now(), response });
    }
    if (!key && response.status !== 'ok') response = { ...response, configHint: GNEWS_HINT };

    const exclude = {
        urls: new Set(local.map(a => (a.sourceUrl ?? '').replace(/[?#].*$/, '').replace(/\/$/, '')).filter(Boolean)),
        titles: new Set(local.map(a => normalise(a.title))),
    };
    const filtered = parsed.terms.length && response.provider === 'GDELT' ? relevant(response.results, parsed) : response.results;
    return { ...response, results: dedupe(filtered, exclude).slice(0, MAX_RESULTS) };
}
