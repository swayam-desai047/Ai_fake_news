import type { Article, ArticleGroup } from './types';

/**
 * Cross-source event matching (handover §6 step 3) for articles that have no backend `group_id`.
 *
 * Headline + lead sentence are vectorised with TF-IDF and compared by cosine similarity.
 * Grouping is seed-based (each article is compared with the group's seed only) so unrelated
 * stories cannot be chained together through a shared middle article. A group is only kept when
 * it contains at least two different publishers. A candidate must also be published within
 * MAX_GAP_HOURS of the seed. Mirrored in backend/services/clustering_service.py.
 *
 * Similarity means "probably the same event"; it is not claim verification.
 */

const STOPWORDS = new Set(
    ('a an the and or but of to in on at for with by from as is are was were be been being it its this that these those after before ' +
        'over under into about than then will would could should may might has have had not no new says say said what how why who whom when ' +
        'where which while amid against more most first last over out up down off just also us uk his her their our your they them he she we ' +
        'you i live latest news video watch report reports year years day days week weeks says one two three can get gets make makes')
        .split(' '),
);

/** Minimum cosine similarity for two reports to be treated as the same event. */
export const SIMILARITY_THRESHOLD = 0.32;
const WINDOW_HOURS = 48;
/** A candidate must be published within this many hours of the group's seed (when both have times). */
export const MAX_GAP_HOURS = 36;

function tokens(text: string): string[] {
    return text
        .toLowerCase()
        .replace(/[’']s\b/g, '')
        .replace(/[^a-z0-9\s-]/g, ' ')
        .split(/\s+/)
        .map(t => t.replace(/^-+|-+$/g, ''))
        .filter(t => t.length > 2 && !STOPWORDS.has(t) && !/^\d+$/.test(t));
}

function leadSentence(text: string): string {
    const m = text.match(/^[\s\S]{0,240}?[.!?](\s|$)/);
    return m ? m[0] : text.slice(0, 240);
}

type Vec = Map<string, number>;

function vectorise(docs: string[][]): Vec[] {
    const df = new Map<string, number>();
    for (const doc of docs) for (const t of new Set(doc)) df.set(t, (df.get(t) ?? 0) + 1);
    const n = docs.length;
    return docs.map(doc => {
        const tf = new Map<string, number>();
        for (const t of doc) tf.set(t, (tf.get(t) ?? 0) + 1);
        const v: Vec = new Map();
        let norm = 0;
        for (const [t, f] of tf) {
            const w = f * Math.log((1 + n) / (1 + (df.get(t) ?? 0)) + 1);
            v.set(t, w);
            norm += w * w;
        }
        norm = Math.sqrt(norm) || 1;
        for (const [t, w] of v) v.set(t, w / norm);
        return v;
    });
}

function cosine(a: Vec, b: Vec): number {
    const [small, large] = a.size < b.size ? [a, b] : [b, a];
    let s = 0;
    for (const [t, w] of small) {
        const o = large.get(t);
        if (o) s += w * o;
    }
    return s;
}

function stableGroupId(members: Article[]): string {
    const key = members.map(m => m.id).sort()[0];
    return `ev-${key.replace(/^lv-/, '')}`;
}

export function clusterArticles(articles: Article[], now = Date.now()): ArticleGroup[] {
    const cutoff = now - WINDOW_HOURS * 3600_000;
    const pool = articles.filter(a => !a.publishedAt || Date.parse(a.publishedAt) >= cutoff);
    if (pool.length < 2) return [];

    const vecs = vectorise(pool.map(a => tokens(`${a.title} ${a.title} ${leadSentence(a.excerpt)}`)));
    const assigned = new Set<number>();
    const groups: ArticleGroup[] = [];

    for (let i = 0; i < pool.length; i++) {
        if (assigned.has(i)) continue;
        const members = [i];
        for (let j = i + 1; j < pool.length; j++) {
            if (assigned.has(j)) continue;
            const ti = Date.parse(pool[i].publishedAt ?? ''), tj = Date.parse(pool[j].publishedAt ?? '');
            if (Number.isFinite(ti) && Number.isFinite(tj) && Math.abs(ti - tj) > MAX_GAP_HOURS * 3600_000) continue;
            if (cosine(vecs[i], vecs[j]) >= SIMILARITY_THRESHOLD) members.push(j);
        }
        const arts = members.map(m => pool[m]);
        // Keep only one report per publisher (the earliest member, i.e. the closest match order).
        const byPublisher = new Map<string, Article>();
        for (const a of arts) if (!byPublisher.has(a.publisher)) byPublisher.set(a.publisher, a);
        if (byPublisher.size < 2) continue;

        const kept = [...byPublisher.values()];
        members.forEach(m => {
            if (kept.includes(pool[m])) assigned.add(m);
        });
        groups.push({
            groupId: stableGroupId(kept),
            eventTitle: pool[i].title,
            articles: kept,
            publishers: kept.map(a => a.publisher),
        });
    }

    return groups.sort((a, b) => b.publishers.length - a.publishers.length);
}
