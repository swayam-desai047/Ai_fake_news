import { supabase, isSupabaseConfigured } from './supabase';
import { getLiveEdition } from './liveNewsService';
import { clusterArticles } from './clustering';
import { riskLabelFor, MIN_EVIDENCE_CHARS } from './scoring';
import { sectionFromCategory, SECTIONS } from './sections';
import { databaseSearchWords, parseQuery, rankArticles } from './search';
import { getExternalArticle, searchExternal, toArticle } from './externalSearch';
import {
    DIMENSION_KEYS,
    type AnalyticsSummary,
    type Article,
    type ArticleGroup,
    type ArticlePage,
    type ArticleQuery,
    type DimensionScores,
    type EditionInfo,
    type RiskLabel,
    type Sentiment,
} from './types';

/**
 * Single server-side entry point for news data.
 *
 * Source order (unchanged from the original app):
 *  1. Supabase `articles` table populated by the FastAPI scheduler, when configured and non-empty.
 *  2. Live publisher RSS feeds, scored with transparent heuristics.
 */

const DB_EDITION_LIMIT = 500;
const DB_CACHE_MS = 60 * 1000;

export interface Edition {
    info: EditionInfo;
    articles: Article[];
    groups: ArticleGroup[];
}

// ─── Supabase row normalisation ────────────────────────────────────────────────────────────

interface ArticleRow {
    id: string;
    title: string;
    source_domain?: string | null;
    source_url?: string | null;
    content_summary?: string | null;
    ai_summary?: string | null;
    category?: string | null;
    sentiment?: string | null;
    is_fake?: boolean | null;
    credibility_score?: number | null;
    risk_score?: number | null;
    confidence_level?: number | null;
    credibility_label?: string | null;
    needs_verification?: boolean | null;
    ai_reasoning?: string | null;
    dimensions?: Record<string, unknown> | null;
    group_id?: string | null;
    event_title?: string | null;
    published_at?: string | null;
    created_at?: string | null;
}

function toDimensions(raw: Record<string, unknown> | null | undefined): DimensionScores | null {
    if (!raw || typeof raw !== 'object') return null;
    const present = DIMENSION_KEYS.filter(k => typeof raw[k] === 'number');
    if (present.length < DIMENSION_KEYS.length) return null;
    const scores = Object.fromEntries(DIMENSION_KEYS.map(k => [k, Math.round(raw[k] as number)]));
    const explanations = (raw.explanations && typeof raw.explanations === 'object' ? raw.explanations : {}) as DimensionScores['explanations'];
    return { ...(scores as Record<(typeof DIMENSION_KEYS)[number], number>), explanations };
}

const RISK_LABELS: RiskLabel[] = ['Low Risk', 'Moderate Risk', 'High Risk'];

function normaliseRow(row: ArticleRow): Article {
    const excerpt = row.content_summary?.trim() ?? '';
    // Pre-migration rows carry only the classifier's `credibility_score`; risk is its complement.
    const riskScore = typeof row.risk_score === 'number'
        ? row.risk_score
        : typeof row.credibility_score === 'number' ? Math.round((1 - row.credibility_score) * 100) / 100 : null;
    const label = RISK_LABELS.includes(row.credibility_label as RiskLabel)
        ? (row.credibility_label as RiskLabel)
        : riskScore !== null ? riskLabelFor(riskScore) : 'Moderate Risk';
    const confidence = typeof row.confidence_level === 'number' ? row.confidence_level : null;
    const needsVerification = typeof row.needs_verification === 'boolean'
        ? row.needs_verification
        : (confidence !== null && confidence >= 0.4 && confidence <= 0.6) || excerpt.length < MIN_EVIDENCE_CHARS;
    const sentiment = (['positive', 'negative', 'neutral'] as Sentiment[]).includes(row.sentiment as Sentiment)
        ? (row.sentiment as Sentiment)
        : null;

    return {
        id: String(row.id),
        title: row.title,
        publisher: row.source_domain?.trim() || 'Unknown publisher',
        sourceUrl: row.source_url || null,
        imageUrl: null,
        excerpt,
        summary: row.ai_summary?.trim() || null,
        summaryKind: row.ai_summary?.trim() ? 'ai' : null,
        section: sectionFromCategory(row.category),
        author: null,
        publishedAt: row.published_at ?? null,
        ingestedAt: row.created_at ?? null,
        sentiment,
        credibility: {
            label,
            score: riskScore,
            confidence,
            needsVerification,
            reasoning: row.ai_reasoning ?? null,
        },
        dimensions: toDimensions(row.dimensions),
        groupId: row.group_id ?? null,
        eventTitle: row.event_title ?? null,
        origin: 'database',
        analysisMethod: 'model',
    };
}

let dbCache: { at: number; articles: Article[] } | null = null;

async function loadDatabaseArticles(): Promise<Article[] | null> {
    if (!isSupabaseConfigured) return null;
    if (dbCache && Date.now() - dbCache.at < DB_CACHE_MS) return dbCache.articles;
    try {
        const { data, error } = await supabase
            .from('articles')
            .select('*')
            .order('published_at', { ascending: false, nullsFirst: false })
            .limit(DB_EDITION_LIMIT);
        if (error || !data || data.length === 0) return null;
        const articles = (data as ArticleRow[]).map(normaliseRow);
        dbCache = { at: Date.now(), articles };
        return articles;
    } catch {
        return null;
    }
}

// ─── Edition ───────────────────────────────────────────────────────────────────────────────

let editionCache: { key: string; edition: Edition } | null = null;

function groupsFromDatabase(articles: Article[]): ArticleGroup[] {
    const map = new Map<string, ArticleGroup>();
    for (const a of articles) {
        if (!a.groupId) continue;
        const g = map.get(a.groupId) ?? { groupId: a.groupId, eventTitle: a.eventTitle || a.title, articles: [], publishers: [] };
        g.articles.push(a);
        if (!g.publishers.includes(a.publisher)) g.publishers.push(a.publisher);
        map.set(a.groupId, g);
    }
    return [...map.values()].filter(g => g.publishers.length >= 2).sort((a, b) => b.publishers.length - a.publishers.length);
}

export async function getEdition(): Promise<Edition> {
    const dbArticles = await loadDatabaseArticles();
    let articles: Article[];
    let fetchedAt: string;
    let failedSources: string[] = [];
    const origin = dbArticles ? 'database' : 'live-feed';

    if (dbArticles) {
        articles = dbArticles;
        fetchedAt = new Date(dbCache?.at ?? Date.now()).toISOString();
    } else {
        const live = await getLiveEdition();
        articles = live.articles;
        fetchedAt = live.fetchedAt;
        failedSources = live.failedSources;
    }

    const key = `${origin}:${fetchedAt}:${articles.length}`;
    if (editionCache?.key === key) return editionCache.edition;

    let groups = origin === 'database' ? groupsFromDatabase(articles) : [];
    if (groups.length === 0) {
        groups = clusterArticles(articles);
        const byId = new Map<string, { groupId: string; eventTitle: string }>();
        for (const g of groups) for (const a of g.articles) byId.set(a.id, { groupId: g.groupId, eventTitle: g.eventTitle });
        articles = articles.map(a => (byId.has(a.id) ? { ...a, ...byId.get(a.id)! } : a));
        groups = groups.map(g => ({ ...g, articles: g.articles.map(a => ({ ...a, ...byId.get(a.id)! })) }));
    }

    const edition: Edition = {
        info: {
            origin,
            fetchedAt,
            articleCount: articles.length,
            publisherCount: new Set(articles.map(a => a.publisher)).size,
            failedSources,
        },
        articles,
        groups,
    };
    editionCache = { key, edition };
    return edition;
}

// ─── Queries ───────────────────────────────────────────────────────────────────────────────

const SINCE_MS: Record<NonNullable<ArticleQuery['since']>, number> = {
    '24h': 24 * 3600_000,
    '7d': 7 * 24 * 3600_000,
    '30d': 30 * 24 * 3600_000,
};

const publishedTime = (a: Article) => Date.parse(a.publishedAt ?? '') || 0;

/** Non-text filters (section, publisher, risk, verification, date). */
function applyFilters(articles: Article[], query: ArticleQuery, now = Date.now()): Article[] {
    let out = articles;
    if (query.section) out = out.filter(a => a.section === query.section);
    if (query.publisher) out = out.filter(a => a.publisher === query.publisher);
    if (query.risk) out = out.filter(a => a.credibility.label === query.risk);
    if (query.needsVerification) out = out.filter(a => a.credibility.needsVerification);
    if (query.since) out = out.filter(a => publishedTime(a) >= now - SINCE_MS[query.since!]);
    return out;
}

/**
 * Filters, then ranks by relevance when there is a search query. Returns the ordered list and how
 * many leading entries match every search term (the rest are partial matches).
 */
export function filterArticles(articles: Article[], query: ArticleQuery, now = Date.now()): { articles: Article[]; fullMatches: number } {
    let out = applyFilters(articles, query, now);
    let fullMatches = out.length;
    if (query.q?.trim()) {
        const ranked = rankArticles(out, parseQuery(query.q));
        out = ranked.map(r => r.article);
        fullMatches = ranked.filter(r => r.kind === 'all').length;
    }
    // Relevance order is kept for searches unless the reader asked for date order explicitly.
    if (query.sort === 'oldest') {
        out = [...out].sort((a, b) => publishedTime(a) - publishedTime(b));
    } else if (!query.q?.trim() || query.sort === 'newest') {
        out = [...out].sort((a, b) => publishedTime(b) - publishedTime(a));
    }
    return { articles: out, fullMatches };
}

const SECTION_CATEGORIES: Partial<Record<string, string[]>> = {
    world: ['general', 'world'],
    technology: ['technology', 'tech'],
    sports: ['sports', 'sport'],
    culture: ['culture', 'entertainment', 'arts'],
};

/**
 * Full-table search in Supabase (not just the cached edition). Candidate rows are those whose
 * headline, excerpt, AI summary or publisher contain any query word; they are then ranked in memory.
 * Search words are reduced to letters, digits and spaces before reaching the filter string.
 */
async function searchDatabase(query: ArticleQuery): Promise<Article[] | null> {
    if (!isSupabaseConfigured || !query.q?.trim()) return null;
    const words = databaseSearchWords(parseQuery(query.q));
    if (words.length === 0) return null;

    const run = async (columns: string[]) => {
        let req = supabase.from('articles').select('*');
        req = req.or(words.flatMap(w => columns.map(c => `${c}.ilike.*${w}*`)).join(','));
        if (query.section) req = req.in('category', SECTION_CATEGORIES[query.section] ?? [query.section]);
        if (query.publisher) req = req.eq('source_domain', query.publisher);
        if (query.since) req = req.gte('published_at', new Date(Date.now() - SINCE_MS[query.since]).toISOString());
        return req.order('published_at', { ascending: false, nullsFirst: false }).limit(400);
    };

    let { data, error } = await run(['title', 'content_summary', 'ai_summary', 'source_domain']);
    // Databases that have not run 01_upgrade_to_msc_synopsis.sql have no ai_summary column.
    if (error) ({ data, error } = await run(['title', 'content_summary', 'source_domain']));
    if (error) throw new Error(`Database search failed: ${error.message}`);
    return ((data ?? []) as ArticleRow[]).map(normaliseRow);
}

export async function queryArticles(query: ArticleQuery): Promise<ArticlePage & { info: EditionInfo }> {
    const edition = await getEdition();
    const limit = Math.min(Math.max(query.limit ?? 20, 1), 100);
    const page = Math.max(query.page ?? 1, 1);

    const pool = edition.info.origin === 'database' ? (await searchDatabase(query)) ?? edition.articles : edition.articles;
    let { articles: all, fullMatches } = filterArticles(pool, query);

    // If query has keywords and we have few or 0 local matches, fetch live news articles directly into results!
    const qTrimmed = query.q?.trim();
    if (qTrimmed && all.length < limit) {
        try {
            const externalResp = await searchExternal(qTrimmed, all, query.since);
            if (externalResp.status === 'ok' && externalResp.results.length > 0) {
                const externalArticles: Article[] = [];
                for (const r of externalResp.results) {
                    const text = [r.title, r.description].filter(Boolean).join('. ');
                    const art = getExternalArticle(r.id) ?? toArticle(r, text);
                    if (art) externalArticles.push(art);
                }
                if (externalArticles.length > 0) {
                    all = [...all, ...externalArticles];
                    fullMatches += externalArticles.length;
                }
            }
        } catch {
            /* fall back to whatever matches exist */
        }
    }

    const start = (page - 1) * limit;
    return {
        articles: all.slice(start, start + limit),
        total: all.length,
        fullMatches,
        page,
        limit,
        hasMore: start + limit < all.length,
        info: edition.info,
    };
}

export async function getArticle(id: string): Promise<{ article: Article; edition: Edition } | null> {
    const edition = await getEdition();
    const found = edition.articles.find(a => a.id === id);
    if (found) return { article: found, edition };

    // An externally discovered report that had enough provider text to be analysed.
    const external = id.startsWith('ex-') ? getExternalArticle(id) : null;
    if (external) return { article: external, edition };

    // A database article older than the cached edition window.
    if (isSupabaseConfigured && !id.startsWith('lv-') && !id.startsWith('ex-')) {
        try {
            const { data } = await supabase.from('articles').select('*').eq('id', id).limit(1);
            if (data && data.length > 0) return { article: normaliseRow(data[0] as ArticleRow), edition };
        } catch {
            /* fall through to not found */
        }
    }
    return null;
}

export async function getGroups(): Promise<{ groups: ArticleGroup[]; info: EditionInfo }> {
    const edition = await getEdition();
    return { groups: edition.groups, info: edition.info };
}

export function relatedArticles(edition: Edition, article: Article, n = 4): Article[] {
    return edition.articles
        .filter(a => a.id !== article.id && a.section === article.section && a.groupId !== article.groupId)
        .slice(0, n);
}

// ─── Analytics ─────────────────────────────────────────────────────────────────────────────

export async function getAnalytics(): Promise<AnalyticsSummary> {
    const edition = await getEdition();
    const { articles, groups } = edition;

    const sections = SECTIONS.map(s => ({ section: s.slug, count: articles.filter(a => a.section === s.slug).length }))
        .filter(s => s.count > 0)
        .sort((a, b) => b.count - a.count);

    const risk: AnalyticsSummary['risk'] = [
        ...RISK_LABELS.map(label => ({ label, count: articles.filter(a => a.credibility.label === label).length })),
        { label: 'Needs Verification', count: articles.filter(a => a.credibility.needsVerification).length },
    ];

    const sentiment: AnalyticsSummary['sentiment'] = (['negative', 'neutral', 'positive'] as Sentiment[]).map(s => ({
        sentiment: s,
        count: articles.filter(a => a.sentiment === s).length,
    }));
    const unscored = articles.filter(a => !a.sentiment).length;
    if (unscored) sentiment.push({ sentiment: 'unscored', count: unscored });

    const scored = articles.filter(a => a.dimensions);
    const dimensionAverages = DIMENSION_KEYS.map(key => ({
        key,
        n: scored.length,
        average: scored.length ? Math.round(scored.reduce((s, a) => s + a.dimensions![key], 0) / scored.length) : 0,
    }));

    const pubCounts = new Map<string, number>();
    for (const a of articles) pubCounts.set(a.publisher, (pubCounts.get(a.publisher) ?? 0) + 1);
    const publishers = [...pubCounts.entries()].map(([publisher, count]) => ({ publisher, count })).sort((a, b) => b.count - a.count);

    // Hourly publication timeline for the most recent 36 hours that contain stories.
    const now = Date.now();
    const buckets = new Map<number, number>();
    for (const a of articles) {
        const t = Date.parse(a.publishedAt ?? '');
        if (!Number.isFinite(t) || t > now || now - t > 36 * 3600_000) continue;
        const h = Math.floor(t / 3600_000) * 3600_000;
        buckets.set(h, (buckets.get(h) ?? 0) + 1);
    }
    const timeline: AnalyticsSummary['timeline'] = [];
    if (buckets.size) {
        const first = Math.min(...buckets.keys());
        for (let h = first; h <= Math.floor(now / 3600_000) * 3600_000; h += 3600_000) {
            timeline.push({ hour: new Date(h).toISOString(), count: buckets.get(h) ?? 0 });
        }
    }

    const ppg = new Map<number, number>();
    for (const g of groups) ppg.set(g.publishers.length, (ppg.get(g.publishers.length) ?? 0) + 1);

    return {
        edition: edition.info,
        sections,
        risk,
        sentiment,
        dimensionAverages,
        publishers,
        timeline,
        coverage: {
            groups: groups.length,
            articlesInGroups: groups.reduce((s, g) => s + g.articles.length, 0),
            largestGroup: groups.reduce((m, g) => Math.max(m, g.publishers.length), 0),
            publishersPerGroup: [...ppg.entries()].map(([publishers, n]) => ({ publishers, groups: n })).sort((a, b) => a.publishers - b.publishers),
        },
        analysisMethods: (['model', 'heuristic'] as const)
            .map(method => ({ method, count: articles.filter(a => a.analysisMethod === method).length }))
            .filter(m => m.count > 0),
    };
}

/** Publisher names present in the current edition, for search filters. */
export async function getPublishers(): Promise<string[]> {
    const edition = await getEdition();
    return [...new Set(edition.articles.map(a => a.publisher))].sort();
}
