import Link from 'next/link';
import type { Article } from '@/lib/types';
import { clockTime, timeAgo } from '@/lib/format';
import { delay } from '@/lib/motion';
import StoryImage from './StoryImage';
import { articleHref, bestSummary, RiskMark, StoryMeta } from './StoryParts';

/** BREAKING NEWS lead: wide photograph, headline beneath, summary, verification and links. */
export function LeadStory({ article }: { article: Article }) {
    const summary = article.summary || bestSummary(article);
    const summaryLabel = article.summaryKind === 'ai' ? 'AI summary' : article.summaryKind === 'extractive' ? 'Extractive summary · sentences selected from the feed' : 'From the publisher';
    return (
        <article>
            <Link href={articleHref(article)} className="story-link">
                <StoryImage article={article} ratio="wide" priority className="enter-img" style={delay(420)} credit />
                <StoryMeta article={article} className="mt-4 enter" />
                <h2 className="hl-lead mt-2 enter" style={delay(520)}>{article.title}</h2>
            </Link>
            {summary && (
                <div className="mt-4 enter" style={delay(600)}>
                    <p className="annotation mb-1.5 uppercase tracking-[0.12em] font-semibold !text-[0.62rem]">{summaryLabel}</p>
                    <p className="dek justify">{summary}</p>
                </div>
            )}
            <div className="mt-4 flex flex-wrap items-center justify-between gap-x-6 gap-y-3 border-t border-[var(--rule)] pt-3 enter" style={delay(660)}>
                <RiskMark credibility={article.credibility} />
                <div className="flex items-center gap-5">
                    <Link href={`${articleHref(article)}#analysis`} className="text-link">Inspect analysis</Link>
                    <Link href={articleHref(article)} className="text-link">Read the story</Link>
                </div>
            </div>
        </article>
    );
}

/** Image-led story for grids: photograph, metadata, headline, summary, reading link. */
export function ImageStory({ article, headline = 'hl-3', summaryChars, showRisk = true, ratio = 'standard' }: {
    article: Article;
    headline?: 'hl-1' | 'hl-2' | 'hl-3';
    summaryChars?: number;
    showRisk?: boolean;
    ratio?: 'standard' | 'wide' | 'square';
}) {
    const summary = bestSummary(article);
    const text = summaryChars && summary.length > summaryChars ? firstSentences(summary, summaryChars) : summary;
    return (
        <article className="flex h-full flex-col">
            <Link href={articleHref(article)} className="story-link">
                <StoryImage article={article} ratio={ratio} />
                <StoryMeta article={article} showSection={false} className="mt-3" />
                <h3 className={`${headline} mt-1.5`}>{article.title}</h3>
            </Link>
            {text && <p className="dek-sm mt-2">{text}</p>}
            <div className="mt-auto flex flex-wrap items-center justify-between gap-2 pt-3">
                {showRisk ? <RiskMark credibility={article.credibility} compact /> : <span />}
                <Link href={articleHref(article)} className="annotation font-semibold !text-[var(--ink)] hover:!text-[var(--red)]">
                    Read <span aria-hidden>→</span>
                </Link>
            </div>
        </article>
    );
}

/** Text-only story with headline, short excerpt and metadata. */
export function TextStory({ article, headline = 'hl-3', withSummary = true, showSection = false, summaryChars = 220 }: {
    article: Article;
    headline?: 'hl-1' | 'hl-2' | 'hl-3' | 'hl-4';
    withSummary?: boolean;
    showSection?: boolean;
    summaryChars?: number;
}) {
    const summary = bestSummary(article);
    return (
        <article>
            <Link href={articleHref(article)} className="story-link">
                <StoryMeta article={article} showSection={showSection} />
                <h3 className={`${headline} mt-1.5`}>{article.title}</h3>
            </Link>
            {withSummary && summary && <p className="dek-sm mt-1.5">{firstSentences(summary, summaryChars)}</p>}
        </article>
    );
}

/** Compact headline with a small thumbnail on the right (used in story rails). */
export function MediaRowStory({ article }: { article: Article }) {
    return (
        <article>
            <Link href={articleHref(article)} className={`story-link ${article.imageUrl ? 'media-row' : ''}`}>
                <div>
                    <StoryMeta article={article} showSection={false} />
                    <h3 className="hl-4 mt-1">{article.title}</h3>
                </div>
                {/* Thumbnails are photographs only; a typographic plate would be illegible at this size. */}
                {article.imageUrl && <StoryImage article={article} ratio="square" />}
            </Link>
        </article>
    );
}

/** LATEST ARTICLES rail entry: marker, time, compact headline, publisher. */
export function RailItem({ article }: { article: Article }) {
    return (
        <li className="rail-item">
            <span className="rail-item__marker" aria-hidden />
            <Link href={articleHref(article)} className="story-link">
                {article.publishedAt && (
                    <time className="rail-item__time" dateTime={article.publishedAt}>{clockTime(article.publishedAt)}</time>
                )}
                <h3 className="hl-4 mt-0.5">{article.title}</h3>
                <p className="meta mt-1 !text-[0.64rem]">{article.publisher}</p>
            </Link>
        </li>
    );
}

/** DAILY FEED entry: category label, headline, short excerpt, publisher and time. */
export function FeedItem({ article }: { article: Article }) {
    const summary = bestSummary(article);
    return (
        <article className="feed-item">
            <Link href={articleHref(article)} className="story-link">
                <StoryMeta article={article} showTime={false} />
                <h3 className="hl-3 mt-1.5">{article.title}</h3>
            </Link>
            {summary && <p className="dek-sm mt-1.5">{firstSentences(summary, 150)}</p>}
            <p className="meta mt-2 !text-[0.64rem]">
                {article.publishedAt ? timeAgo(article.publishedAt) : 'Undated'}
                {article.credibility.needsVerification && <span className="meta-sep !text-[var(--risk-verify)]">Needs verification</span>}
            </p>
        </article>
    );
}

/**
 * Shorten to whole sentences where possible so excerpts never stop mid-thought; falls back to a
 * word boundary for single long sentences.
 */
export function firstSentences(text: string, maxChars: number): string {
    if (text.length <= maxChars) return text;
    const sentences = text.match(/[^.!?]+[.!?]+["'’”]?\s*/g) ?? [];
    let out = '';
    for (const s of sentences) {
        if ((out + s).length > maxChars) break;
        out += s;
    }
    if (out.trim().length >= maxChars * 0.45) return out.trim();
    const cut = text.slice(0, maxChars);
    return `${cut.slice(0, cut.lastIndexOf(' '))}…`;
}
