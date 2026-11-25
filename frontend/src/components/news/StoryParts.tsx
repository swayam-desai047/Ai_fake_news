import Link from 'next/link';
import type { ReactNode } from 'react';
import type { Article, CredibilityAssessment } from '@/lib/types';
import { sectionLabel } from '@/lib/sections';
import { timeAgo } from '@/lib/format';

export function articleHref(a: Pick<Article, 'id'>): string {
    return `/article/${encodeURIComponent(a.id)}`;
}

const RISK_CLASS: Record<CredibilityAssessment['label'], string> = {
    'Low Risk': 'risk risk--low',
    'Moderate Risk': 'risk risk--moderate',
    'High Risk': 'risk risk--high',
    Unavailable: 'risk risk--unavailable',
};

/** Credibility-risk label, with the separate "Needs Verification" state beside it. */
export function RiskMark({ credibility, compact = false }: { credibility: CredibilityAssessment; compact?: boolean }) {
    return (
        <span className="inline-flex flex-wrap items-center gap-x-3 gap-y-1">
            <span
                className={RISK_CLASS[credibility.label]}
                title={credibility.label === 'Unavailable'
                    ? 'No risk score: too little text to assess, or analysis not yet available'
                    : 'Credibility-risk indicator (AI-generated, not a verdict)'}
            >
                <span className="risk__dot" aria-hidden />
                {credibility.label === 'Unavailable' ? (compact ? 'Not assessed' : 'Risk not assessed') : credibility.label}
            </span>
            {credibility.needsVerification && (
                <span className="risk risk--verify" title="Too little evidence or an ambiguous score — check the original report">
                    <span className="risk__dot" aria-hidden />
                    {compact ? 'Verify' : 'Needs verification'}
                </span>
            )}
        </span>
    );
}

/** Kicker line: SECTION · PUBLISHER · TIME. */
export function StoryMeta({ article, showSection = true, showTime = true, className = '' }: {
    article: Article;
    showSection?: boolean;
    showTime?: boolean;
    className?: string;
}) {
    return (
        <p className={`flex flex-wrap items-baseline ${className}`}>
            {showSection && <span className="kicker">{sectionLabel(article.section)}</span>}
            <span className={`meta ${showSection ? 'meta-sep' : ''}`}>{article.publisher}</span>
            {showTime && article.publishedAt && (
                <time className="meta meta-sep" dateTime={article.publishedAt}>{timeAgo(article.publishedAt)}</time>
            )}
        </p>
    );
}

export function SectionHeading({ title, href, more = 'More', serif = false, id, children }: {
    title: string;
    href?: string;
    more?: string;
    serif?: boolean;
    id?: string;
    children?: ReactNode;
}) {
    return (
        <div className="section-head">
            <h2 id={id} className={`section-head__title ${serif ? 'section-head__title--serif' : ''}`}>{title}</h2>
            {children}
            {href && (
                <Link href={href} className="section-head__more">
                    {more} <span aria-hidden>→</span>
                </Link>
            )}
        </div>
    );
}

/** The text that stands in for a summary: AI summary, or the first paragraph of the publisher excerpt. */
export function bestSummary(a: Article): string {
    if (a.summaryKind === 'ai' && a.summary) return a.summary;
    return paragraphs(a.excerpt)[0] ?? '';
}

export function paragraphs(text: string | null | undefined): string[] {
    return (text ?? '').split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
}
