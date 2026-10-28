import Link from 'next/link';
import type { Article } from '@/lib/types';
import { sectionLabel } from '@/lib/sections';
import { dateTime, pct } from '@/lib/format';
import StoryImage from '@/components/news/StoryImage';
import { articleHref, bestSummary, RiskMark } from '@/components/news/StoryParts';

interface NewsCardProps {
    article: Article;
    /** Show the section label (off on section fronts, where it is implied). */
    showSection?: boolean;
}

/**
 * A story as it appears in search results and section listings: a printed index entry with
 * headline, dek, provenance and credibility indicators, and the publisher's photograph at right.
 */
export default function NewsCard({ article, showSection = true }: NewsCardProps) {
    const summary = bestSummary(article);
    const { credibility } = article;
    return (
        <article className="grid gap-x-6 gap-y-3 py-5 border-b border-[var(--rule)] sm:grid-cols-[minmax(0,1fr)_200px]">
            <div className="min-w-0">
                <p className="flex flex-wrap items-baseline">
                    {showSection && <span className="kicker">{sectionLabel(article.section)}</span>}
                    <span className={`meta ${showSection ? 'meta-sep' : ''}`}>{article.publisher}</span>
                    {article.publishedAt && <time className="meta meta-sep" dateTime={article.publishedAt}>{dateTime(article.publishedAt)}</time>}
                </p>
                <Link href={articleHref(article)} className="story-link mt-1.5">
                    <h3 className="hl-2">{article.title}</h3>
                </Link>
                {summary && <p className="dek-sm mt-2 max-w-[68ch]">{summary}</p>}
                <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1">
                    <RiskMark credibility={credibility} />
                    <span className="annotation">
                        Confidence {credibility.confidence !== null ? pct(credibility.confidence) : 'not reported'}
                    </span>
                    <Link href={`${articleHref(article)}#analysis`} className="annotation font-semibold !text-[var(--ink)] hover:!text-[var(--red)]">
                        Analysis <span aria-hidden>→</span>
                    </Link>
                </div>
            </div>
            {article.imageUrl && (
                <Link href={articleHref(article)} className="story-link order-first sm:order-none" tabIndex={-1} aria-hidden>
                    <StoryImage article={article} />
                </Link>
            )}
        </article>
    );
}
