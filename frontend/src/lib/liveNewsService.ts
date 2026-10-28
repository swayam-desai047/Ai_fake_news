import { SECTIONS, type FeedSource } from './sections';
import { analyseText, extractiveSummary } from './scoring';
import type { Article, SectionSlug } from './types';

/**
 * Live edition: reads publishers' own RSS feeds directly (BBC, The Guardian, The Hindu, NDTV,
 * The Indian Express, Mint, Al Jazeera, TechCrunch). Used whenever the Supabase table written by
 * the FastAPI pipeline is not configured or is empty.
 *
 * Only what the feed supplies is kept: headline, link, excerpt, image, date and byline.
 * Articles are scored with the transparent heuristics in `scoring.ts`.
 */

const ITEMS_PER_FEED = 20;
const CACHE_TTL_MS = 2 * 60 * 1000;
const FETCH_TIMEOUT_MS = 8000;

export interface LiveEdition {
    articles: Article[];
    fetchedAt: string;
    failedSources: string[];
}

let cache: { at: number; edition: LiveEdition } | null = null;
let inflight: Promise<LiveEdition> | null = null;

const ENTITIES: Record<string, string> = {
    amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', hellip: '…', mdash: '—', ndash: '–',
    lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”', pound: '£', euro: '€', rupee: '₹',
};

function decodeEntities(s: string): string {
    return s.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (m, code: string) => {
        if (code[0] === '#') {
            const n = code[1].toLowerCase() === 'x' ? parseInt(code.slice(2), 16) : parseInt(code.slice(1), 10);
            return Number.isFinite(n) ? String.fromCodePoint(n) : m;
        }
        return ENTITIES[code.toLowerCase()] ?? m;
    });
}

function unwrapCdata(s: string): string {
    return s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1');
}

/** Plain text from an RSS field that may hold escaped or raw HTML. Paragraph breaks become "\n\n". */
export function cleanText(raw: string | undefined | null): string {
    if (!raw) return '';
    let t = decodeEntities(unwrapCdata(raw));
    t = t.replace(/<a [^>]*>\s*Continue reading\.*\s*<\/a>/gi, '');
    t = t.replace(/<\/p>\s*<p[^>]*>|<br\s*\/?>/gi, '\n\n');
    t = t.replace(/<[^>]*>/g, ' ');
    t = decodeEntities(t).replace(/\s*Continue reading\.{0,3}\s*$/i, '');
    return t
        .split(/\n{2,}/)
        .map(p => p.replace(/\s+/g, ' ').trim())
        .filter(Boolean)
        .join('\n\n');
}

function tag(xml: string, name: string): string | undefined {
    const re = new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)</${name}>`, 'i');
    return xml.match(re)?.[1];
}

function bestImage(item: string): string | null {
    const candidates: { url: string; width: number }[] = [];
    const re = /<(media:content|media:thumbnail|enclosure)\b([^>]*?)\/?>/gi;
    let m: RegExpExecArray | null;
    while ((m = re.exec(item))) {
        const attrs = m[2];
        const url = attrs.match(/url="([^"]+)"/i)?.[1];
        if (!url) continue;
        const type = attrs.match(/(?:type|medium)="([^"]+)"/i)?.[1] ?? 'image';
        if (!/image|jpe?g|png|webp/i.test(type) && !/\.(jpe?g|png|webp)/i.test(url)) continue;
        const width = parseInt(attrs.match(/width="(\d+)"/i)?.[1] ?? '0', 10);
        candidates.push({ url: decodeEntities(url), width });
    }
    if (candidates.length === 0) return null;
    candidates.sort((a, b) => b.width - a.width);
    let url = candidates[0].url;
    // BBC feeds publish 240px thumbnails; the same asset is served at larger standard widths.
    url = url.replace(/(ichef\.bbci\.co\.uk\/(?:ace|news)\/(?:standard|ws))\/\d+\//, '$1/976/');
    return url;
}

/** Deterministic short id so the same story keeps the same URL across refreshes. */
export function hashId(input: string): string {
    let h1 = 0xdeadbeef ^ input.length;
    let h2 = 0x41c6ce57 ^ input.length;
    for (let i = 0; i < input.length; i++) {
        const ch = input.charCodeAt(i);
        h1 = Math.imul(h1 ^ ch, 2654435761);
        h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
}

function canonicalLink(link: string): string {
    return link.replace(/[?#].*$/, '').replace(/\/$/, '');
}

function parseDate(raw: string | undefined): string | null {
    if (!raw) return null;
    const t = Date.parse(cleanText(raw));
    return Number.isFinite(t) ? new Date(t).toISOString() : null;
}

function parseFeed(xml: string, source: FeedSource, section: SectionSlug, fetchedAt: string): Article[] {
    const items = xml.match(/<item\b[\s\S]*?<\/item>/gi) ?? [];
    const out: Article[] = [];
    for (const item of items.slice(0, ITEMS_PER_FEED)) {
        let title = cleanText(tag(item, 'title'));
        const link = cleanText(tag(item, 'link'));
        if (!title || !link) continue;

        let publisher = source.publisher;
        const sourceMatch = item.match(/<source[^>]*>([\s\S]*?)<\/source>/i);
        const sourceName = sourceMatch ? cleanText(sourceMatch[1]) : '';
        if (sourceName) {
            publisher = sourceName;
            if (title.endsWith(` - ${sourceName}`)) {
                title = title.slice(0, -(sourceName.length + 3)).trim();
            }
        } else if (title.includes(' - ')) {
            const parts = title.split(' - ');
            const candidate = parts[parts.length - 1].trim();
            if (candidate.length > 1 && candidate.length < 35) {
                publisher = candidate;
                title = parts.slice(0, -1).join(' - ').trim();
            }
        }

        let excerpt = cleanText(tag(item, 'description'));
        if (!excerpt) excerpt = cleanText(tag(item, 'content:encoded'));
        if (excerpt.toLowerCase() === title.toLowerCase()) excerpt = '';

        const author = cleanText(tag(item, 'dc:creator')) || null;
        const analysis = analyseText(title, excerpt, publisher);
        const summary = extractiveSummary(excerpt);

        out.push({
            id: `lv-${hashId(canonicalLink(link))}`,
            title,
            publisher,
            sourceUrl: link,
            imageUrl: bestImage(item),
            excerpt,
            summary,
            summaryKind: summary ? 'extractive' : null,
            section,
            author,
            publishedAt: parseDate(tag(item, 'pubDate') ?? tag(item, 'dc:date')),
            ingestedAt: fetchedAt,
            sentiment: analysis.sentiment,
            credibility: analysis.credibility,
            dimensions: analysis.dimensions,
            groupId: null,
            eventTitle: null,
            origin: 'live-feed',
            analysisMethod: 'heuristic',
        });
    }
    return out;
}

async function fetchFeed(source: FeedSource, section: SectionSlug, fetchedAt: string): Promise<Article[]> {
    const res = await fetch(source.url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' },
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
        next: { revalidate: 120 },
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return parseFeed(await res.text(), source, section, fetchedAt);
}

async function buildEdition(): Promise<LiveEdition> {
    const fetchedAt = new Date().toISOString();
    const jobs = SECTIONS.flatMap(section =>
        section.feeds.map(feed => ({ feed, section: section.slug })),
    );
    const results = await Promise.allSettled(jobs.map(j => fetchFeed(j.feed, j.section, fetchedAt)));

    const seen = new Set<string>();
    const articles: Article[] = [];
    const failedSources: string[] = [];
    results.forEach((r, i) => {
        if (r.status === 'rejected') {
            failedSources.push(`${jobs[i].feed.publisher} (${jobs[i].section})`);
            return;
        }
        for (const a of r.value) {
            const titleKey = `${a.publisher}::${a.title.toLowerCase()}`;
            if (seen.has(a.id) || seen.has(titleKey)) continue;
            seen.add(a.id);
            seen.add(titleKey);
            articles.push(a);
        }
    });

    articles.sort((a, b) => (Date.parse(b.publishedAt ?? '') || 0) - (Date.parse(a.publishedAt ?? '') || 0));
    return { articles, fetchedAt, failedSources };
}

export async function getLiveEdition(): Promise<LiveEdition> {
    if (cache && Date.now() - cache.at < CACHE_TTL_MS) return cache.edition;
    if (!inflight) {
        inflight = buildEdition()
            .then(edition => {
                if (edition.articles.length > 0) cache = { at: Date.now(), edition };
                return edition;
            })
            .finally(() => {
                inflight = null;
            });
    }
    return inflight;
}
