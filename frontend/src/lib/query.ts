import { getSection } from './sections';
import type { ArticleQuery, CredibilityLabel } from './types';

const RISKS: CredibilityLabel[] = ['Low Risk', 'Moderate Risk', 'High Risk', 'Unavailable'];

type Params = URLSearchParams | Record<string, string | string[] | undefined>;

function read(params: Params, key: string): string {
    if (params instanceof URLSearchParams) return params.get(key) ?? '';
    const v = params[key];
    return typeof v === 'string' ? v : Array.isArray(v) ? v[0] ?? '' : '';
}

/** Parses search/filter parameters shared by the search page and `/api/articles`. */
export function parseArticleQuery(params: Params): ArticleQuery {
    const sectionRaw = read(params, 'section') || read(params, 'category');
    const risk = read(params, 'risk');
    const sort = read(params, 'sort');
    const since = read(params, 'since');
    const page = parseInt(read(params, 'page') || '1', 10);
    const limit = parseInt(read(params, 'limit') || '20', 10);
    return {
        q: read(params, 'q').trim().slice(0, 120),
        section: getSection(sectionRaw)?.slug ?? '',
        publisher: read(params, 'publisher'),
        risk: RISKS.includes(risk as CredibilityLabel) ? (risk as CredibilityLabel) : '',
        needsVerification: read(params, 'verify') === '1',
        sort: sort === 'oldest' || sort === 'newest' || sort === 'relevance' ? sort : undefined,
        since: since === '24h' || since === '7d' || since === '30d' ? since : undefined,
        page: Number.isFinite(page) && page > 0 ? page : 1,
        limit: Number.isFinite(limit) ? limit : 20,
    };
}

export function queryToParams(q: ArticleQuery): URLSearchParams {
    const p = new URLSearchParams();
    if (q.q) p.set('q', q.q);
    if (q.section) p.set('section', q.section);
    if (q.publisher) p.set('publisher', q.publisher);
    if (q.risk) p.set('risk', q.risk);
    if (q.needsVerification) p.set('verify', '1');
    if (q.sort) p.set('sort', q.sort);
    if (q.since) p.set('since', q.since);
    return p;
}
