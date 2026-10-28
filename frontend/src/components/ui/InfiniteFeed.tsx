"use client";

import React, { useState } from 'react';
import NewsCard from '@/components/ui/NewsCard';
import type { Article, ArticlePage } from '@/lib/types';

interface InfiniteFeedProps {
    initialArticles: Article[];
    /** Query string for `/api/articles` (filters only — paging is added here). */
    query?: string;
    /** When the full list is already known (section fronts), page through it locally instead. */
    localPool?: Article[];
    initialPage: number;
    pageSize: number;
    hasMore: boolean;
    showSection?: boolean;
    /** For searches: entries from this index on are partial matches and get a divider. */
    fullMatches?: number;
}

/** Story listing with a "load more" control backed by `/api/articles`. */
export default function InfiniteFeed({ initialArticles, query = '', localPool, initialPage, pageSize, hasMore: initialHasMore, showSection = true, fullMatches }: InfiniteFeedProps) {
    const [articles, setArticles] = useState(initialArticles);
    const [page, setPage] = useState(initialPage);
    const [hasMore, setHasMore] = useState(initialHasMore);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const loadMore = async () => {
        if (loading || !hasMore) return;
        setLoading(true);
        setError('');
        const nextPage = page + 1;
        if (localPool) {
            setArticles(localPool.slice(0, nextPage * pageSize));
            setHasMore(localPool.length > nextPage * pageSize);
            setPage(nextPage);
            setLoading(false);
            return;
        }
        try {
            const params = new URLSearchParams(query);
            params.set('page', String(nextPage));
            params.set('limit', String(pageSize));
            const res = await fetch(`/api/articles?${params.toString()}`);
            if (!res.ok) throw new Error(String(res.status));
            const data = (await res.json()) as ArticlePage;
            setArticles(prev => {
                const seen = new Set(prev.map(a => a.id));
                return [...prev, ...data.articles.filter(a => !seen.has(a.id))];
            });
            setHasMore(data.hasMore);
            setPage(nextPage);
        } catch {
            setError('More stories could not be loaded. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div aria-live="polite">
                {articles.map((article, i) => (
                    <div key={article.id}>
                        {fullMatches !== undefined && i === fullMatches && fullMatches > 0 && (
                            <p className="section-head__title border-b border-[var(--ink)] pb-2 mt-8">Partial matches · some of your terms</p>
                        )}
                        <NewsCard article={article} showSection={showSection} />
                    </div>
                ))}
            </div>

            {error && <p role="alert" className="annotation !text-[var(--red)] mt-4 text-center">{error}</p>}

            {hasMore && (
                <div className="mt-8 text-center">
                    <button type="button" onClick={loadMore} disabled={loading} className="btn btn--ghost min-w-56">
                        {loading ? 'Setting more type…' : 'Load more stories'}
                    </button>
                </div>
            )}
            {!hasMore && articles.length > pageSize && (
                <p className="annotation text-center mt-8 italic">End of the edition&rsquo;s matching stories.</p>
            )}
        </div>
    );
}
