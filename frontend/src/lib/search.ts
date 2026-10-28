import type { Article } from './types';

/**
 * Relevance search over articles.
 *
 * Fixes the original "every word must appear verbatim" filter, which returned nothing for
 * queries such as "Facebook lawsuit 2026":
 *  - case, accents and punctuation are normalised away;
 *  - matching is per word (word-prefix, so "elect" finds "election") — never inside other words,
 *    so "meta" no longer matches "metal";
 *  - simple plural/suffix stemming ("lawsuits" ↔ "lawsuit");
 *  - a small alias table for renamed organisations ("facebook" ↔ "meta");
 *  - a four-digit year is a date hint (matches the publication year or the text), not a required word;
 *  - results are ranked: headline > publisher > summary/excerpt, with a bonus for the whole phrase.
 * When no report contains every term, the closest partial matches are returned and labelled as such.
 */

const STOPWORDS = new Set(
    'a an and the of to in on at for with by from as is are was were be been it its this that these those or not no about into over after before news latest today report reports story stories article articles'.split(' '),
);

/** Organisations commonly searched by an old or alternative name. Each group is matched as one term. */
const ALIASES: string[][] = [
    ['facebook', 'meta'],
    ['google', 'alphabet'],
    ['un', 'united nations'],
    ['uk', 'britain', 'british'],
    ['us', 'usa', 'america', 'american'],
];

export function normalise(text: string): string {
    return text
        .normalize('NFKD')
        .replace(/[̀-ͯ]/g, '')
        .toLowerCase()
        .replace(/[’‘`´]/g, "'")
        .replace(/'s\b/g, '')
        .replace(/[^a-z0-9]+/g, ' ')
        .trim();
}

export function stem(word: string): string {
    if (word.length <= 4 || /^\d+$/.test(word)) return word;
    if (word.endsWith('ies')) return `${word.slice(0, -3)}y`;
    if (word.endsWith('sses')) return word.slice(0, -2);
    if (/(ches|shes|xes|zes)$/.test(word)) return word.slice(0, -2);
    if (word.endsWith('s') && !word.endsWith('ss') && !word.endsWith('us')) return word.slice(0, -1);
    return word;
}

export interface ParsedQuery {
    raw: string;
    /** Each term is a set of interchangeable alternatives (a word plus its aliases). */
    terms: string[][];
    years: number[];
    phrase: string;
}

export function parseQuery(q: string): ParsedQuery {
    const phrase = normalise(q);
    const words = phrase.split(' ').filter(Boolean);
    const years = words.filter(w => /^(19|20)\d{2}$/.test(w)).map(Number);
    const terms: string[][] = [];
    for (const w of words) {
        // Years become a date hint; stopwords and single letters (e.g. the "d" of "d'Or") are not search terms.
        if (/^(19|20)\d{2}$/.test(w) || STOPWORDS.has(w) || w.length < 2) continue;
        const s = stem(w);
        const group = ALIASES.find(g => g.includes(w) || g.includes(s));
        const alts = group ? [...new Set([s, ...group.map(stem)])] : [s];
        if (!terms.some(t => t.join() === alts.join())) terms.push(alts);
    }
    // A query of only stopwords still searches for what was typed.
    if (terms.length === 0 && years.length === 0 && words.length) terms.push([stem(words[0])]);
    return { raw: q, terms, years, phrase };
}

function tokenise(text: string): string[] {
    return normalise(text).split(' ').filter(Boolean).map(stem);
}

/**
 * A query alternative matches a field when one of the field's words equals it or starts with it
 * ("electi" → "election"). Terms of three letters or fewer must match a whole word; four-letter terms
 * may only be extended by two or more letters, so "memo" finds "memoir" but "meta" never matches "metal".
 */
function fieldHas(tokens: string[], joined: string, alt: string): boolean {
    if (alt.includes(' ')) return ` ${joined} `.includes(` ${alt} `);
    if (alt.length <= 3) return tokens.includes(alt);
    if (alt.length === 4) return tokens.some(t => t === alt || (t.length >= 6 && t.startsWith(alt)));
    return tokens.some(t => t.startsWith(alt));
}

export type MatchKind = 'all' | 'partial';

export interface RankedArticle {
    article: Article;
    score: number;
    matched: number;
    kind: MatchKind;
}

export function rankArticles(articles: Article[], parsed: ParsedQuery): RankedArticle[] {
    const { terms, years, phrase } = parsed;
    const needed = terms.length;
    const out: RankedArticle[] = [];

    for (const article of articles) {
        const fields = [
            { tokens: tokenise(article.title), weight: 3 },
            { tokens: tokenise(article.publisher), weight: 2 },
            { tokens: tokenise(`${article.summary ?? ''} ${article.excerpt} ${article.eventTitle ?? ''}`), weight: 1 },
        ].map(f => ({ ...f, joined: f.tokens.join(' ') }));

        let score = 0;
        let matched = 0;
        for (const alts of terms) {
            let best = 0;
            for (const f of fields) {
                if (alts.some(alt => fieldHas(f.tokens, f.joined, alt))) best = Math.max(best, f.weight);
            }
            if (best > 0) {
                matched++;
                score += best;
            }
        }

        let yearOk = true;
        if (years.length) {
            const published = article.publishedAt ? new Date(article.publishedAt).getUTCFullYear() : null;
            const inText = years.some(y => fields.some(f => f.tokens.includes(String(y))));
            yearOk = (published !== null && years.includes(published)) || inText;
            if (yearOk) score += 0.5;
        }

        if (needed === 0) {
            if (yearOk) out.push({ article, score, matched: 0, kind: 'all' });
            continue;
        }
        if (matched === 0 || !yearOk) continue;
        if (phrase.length > 3 && normalise(article.title).includes(phrase)) score += 5;

        const kind: MatchKind = matched === needed ? 'all' : 'partial';
        // Partial matches must cover at least half of the terms.
        if (kind === 'partial' && matched < Math.ceil(needed / 2)) continue;
        out.push({ article, score, matched, kind });
    }

    const time = (a: Article) => Date.parse(a.publishedAt ?? '') || 0;
    return out.sort((a, b) => (a.kind === b.kind ? 0 : a.kind === 'all' ? -1 : 1) || b.score - a.score || time(b.article) - time(a.article));
}

/** Search words safe to embed in a PostgREST `ilike` filter (letters, digits and single spaces only). */
export function databaseSearchWords(parsed: ParsedQuery): string[] {
    return [...new Set(parsed.terms.flat())].filter(w => /^[a-z0-9 ]+$/.test(w)).slice(0, 12);
}
