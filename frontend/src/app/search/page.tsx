import type { Metadata } from 'next';
import { getPublishers, queryArticles } from '@/lib/repository';
import { parseArticleQuery, queryToParams } from '@/lib/query';
import { sectionLabel } from '@/lib/sections';
import SearchAndFilter from '@/components/ui/SearchAndFilter';
import InfiniteFeed from '@/components/ui/InfiniteFeed';
import ExternalResults from '@/components/ui/ExternalResults';
import { clockTime, EDITION_TZ_LABEL } from '@/lib/format';

export const metadata: Metadata = { title: 'Search' };

const PAGE_SIZE = 20;
/** External discovery starts automatically when fewer local reports than this match every term. */
const AUTO_EXTERNAL_BELOW = 5;

export default async function SearchPage(props: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
    const query = parseArticleQuery(await props.searchParams);
    query.limit = PAGE_SIZE;
    query.page = 1;

    let result: Awaited<ReturnType<typeof queryArticles>> | null = null;
    let publishers: string[] = [];
    let searchError = '';
    try {
        [result, publishers] = await Promise.all([queryArticles(query), getPublishers()]);
    } catch (err) {
        console.error('Search failed:', err);
        searchError = err instanceof Error && err.message.startsWith('Database') ? 'database query failed' : '';
        result = null;
    }

    const hasQuery = Boolean(query.q?.trim());
    const sortLabel = query.sort === 'oldest' ? 'Oldest first' : query.sort === 'newest' || !hasQuery ? 'Newest first' : 'Most relevant first';
    const scope = result
        ? result.info.origin === 'database'
            ? 'Searched the full ingestion database: headlines, excerpts, AI summaries and publisher names.'
            : `Searched all ${result.info.articleCount} reports in today\u2019s edition (live publisher feeds, fetched ${clockTime(result.info.fetchedAt)} ${EDITION_TZ_LABEL}): headlines, excerpts and publisher names.`
        : '';

    const described = [
        query.q && `“${query.q}”`,
        query.section && sectionLabel(query.section),
        query.publisher,
        query.risk,
        query.needsVerification && 'needing verification',
        query.since && { '24h': 'last 24 hours', '7d': 'last 7 days', '30d': 'last 30 days' }[query.since],
    ].filter(Boolean);

    return (
        <div className="np-container pt-8">
            <header className="mb-6">
                <p className="kicker">Search</p>
                <h1 className="hl-lead mt-2 enter">Search the edition</h1>
                <p className="dek mt-3 max-w-2xl enter" style={{ '--d': '80ms' } as React.CSSProperties}>
                    Every report in today&rsquo;s edition, searchable by headline and text, and filterable by section,
                    publisher and credibility indicators.
                </p>
            </header>

            <SearchAndFilter query={query} publishers={publishers} />

            {!result ? (
                <div className="notice mt-10" role="alert">
                    <h2 className="hl-2">Search is temporarily unavailable</h2>
                    <p className="dek-sm mt-2">
                        The server could not complete the search{searchError ? ` (${searchError})` : ''}. This is a service error,
                        not an empty result. Please try again in a moment.
                    </p>
                </div>
            ) : (
                <section className="mt-6" aria-labelledby="results-h">
                    <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--ink)] pb-2">
                        <h2 id="results-h" className="section-head__title">
                            {hasQuery ? `${result.fullMatches} ${result.fullMatches === 1 ? 'report matches' : 'reports match'} every term` : `${result.total} ${result.total === 1 ? 'report' : 'reports'}`}
                            {described.length > 0 && <span className="font-normal normal-case tracking-normal font-serif italic text-[var(--ink-2)]"> — {described.join(' · ')}</span>}
                        </h2>
                        <p className="annotation">{sortLabel}</p>
                    </div>
                    <p className="annotation mt-2">{scope}</p>
                    {result.total === 0 ? (
                        <div className="py-10 text-center border-b border-[var(--rule)]">
                            <p className="hl-2">No reports in {result.info.origin === 'database' ? 'the database' : 'today\u2019s edition'} match.</p>
                            <p className="dek-sm mt-2">
                                {hasQuery ? 'Other news sources are searched below.' : 'Try another section, or clear the filters.'}
                            </p>
                        </div>
                    ) : (
                        <>
                            {hasQuery && result.fullMatches === 0 && (
                                <p className="dek-sm italic mt-4">
                                    No report contains every term. The closest partial matches, containing at least half of your terms, are shown below.
                                </p>
                            )}
                            <InfiniteFeed
                                key={queryToParams(query).toString()}
                                initialArticles={result.articles}
                                query={queryToParams(query).toString()}
                                initialPage={1}
                                pageSize={PAGE_SIZE}
                                hasMore={result.hasMore}
                                fullMatches={hasQuery ? result.fullMatches : undefined}
                            />
                        </>
                    )}
                    {hasQuery && (
                        <ExternalResults key={`${query.q}:${query.since ?? ''}`} q={query.q!} since={query.since} autoRun={result.fullMatches < AUTO_EXTERNAL_BELOW} />
                    )}
                </section>
            )}
        </div>
    );
}
