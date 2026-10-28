import Link from 'next/link';
import { ExternalLink } from 'lucide-react';
import type { ArticleGroup } from '@/lib/types';
import { clockTime, dateTime } from '@/lib/format';
import { DIMENSIONS } from '@/lib/dimensions';
import { sectionLabel } from '@/lib/sections';
import { articleHref, paragraphs, RiskMark } from '@/components/news/StoryParts';
import StoryImage from '@/components/news/StoryImage';
import Reveal from '@/components/motion/Reveal';

const TONE: Record<string, string> = { positive: 'Positive tone', negative: 'Negative tone', neutral: 'Neutral tone' };
const COMPARE_KEYS = ['sentiment', 'objectivity', 'propaganda', 'headline_accuracy'] as const;

/**
 * One event, set as a newspaper comparison spread: each publisher gets a column with its own
 * headline, timing, summary, tone and indicators, so differences in framing can be scanned across.
 */
export default function CrossSourceView({ group, index }: { group: ArticleGroup; index: number }) {
    const sorted = [...group.articles].sort((a, b) => (Date.parse(a.publishedAt ?? '') || 0) - (Date.parse(b.publishedAt ?? '') || 0));
    const firstAt = sorted[0]?.publishedAt;
    const cols = Math.min(sorted.length, 4);
    const lead = sorted.find(a => a.imageUrl);

    return (
        <Reveal as="section" id={group.groupId} className="mt-14 scroll-mt-20" aria-labelledby={`${group.groupId}-h`}>
            <div className="flex flex-wrap items-baseline justify-between gap-3 border-b-2 border-[var(--ink)] pb-2">
                <p className="kicker">Event {index + 1} · {sectionLabel(sorted[0].section)} · {group.publishers.length} publishers</p>
                {firstAt && <p className="annotation">First reported {dateTime(firstAt)}</p>}
            </div>

            <div className="mt-4 grid gap-6 md:grid-cols-[minmax(0,1fr)_260px] items-start">
                <h2 id={`${group.groupId}-h`} className="hl-1">{group.eventTitle}</h2>
                {lead && <StoryImage article={lead} ratio="standard" credit className="hidden md:block" />}
            </div>

            <div className="spread mt-5 border-t border-[var(--ink)]" style={{ '--spread-cols': cols } as React.CSSProperties}>
                {sorted.map((a, i) => {
                    const first = paragraphs(a.summary || a.excerpt)[0];
                    return (
                        <article key={a.id} className="flex flex-col">
                            <p className="flex items-baseline justify-between gap-2">
                                <span className="font-[family-name:var(--font-display)] italic font-bold text-lg leading-tight">{a.publisher}</span>
                                <span className="meta whitespace-nowrap">{i === 0 ? 'First · ' : ''}{clockTime(a.publishedAt)}</span>
                            </p>
                            <Link href={articleHref(a)} className="story-link mt-2">
                                <h3 className="hl-3">&ldquo;{a.title}&rdquo;</h3>
                            </Link>
                            {first && <p className="dek-sm mt-2">{first}</p>}
                            <dl className="mt-4 border-t border-[var(--rule)] pt-2 space-y-1.5 annotation">
                                <div className="flex justify-between gap-2"><dt>Tone</dt><dd className="font-semibold !text-[var(--ink)]">{a.sentiment ? TONE[a.sentiment] : 'Not scored'}</dd></div>
                                {a.dimensions && COMPARE_KEYS.map(k => {
                                    const meta = DIMENSIONS.find(d => d.key === k)!;
                                    return (
                                        <div key={k} className="grid grid-cols-[1fr_56px_24px] items-center gap-2">
                                            <dt>{meta.short}</dt>
                                            <dd className="score-bar" aria-hidden><span className="score-bar__fill" style={{ width: `${a.dimensions![k]}%` }} /></dd>
                                            <dd className="text-right font-semibold !text-[var(--ink)]">{a.dimensions![k]}</dd>
                                        </div>
                                    );
                                })}
                            </dl>
                            <div className="mt-auto pt-3 flex flex-wrap items-center justify-between gap-2">
                                <RiskMark credibility={a.credibility} compact />
                                {a.sourceUrl && (
                                    <a href={a.sourceUrl} target="_blank" rel="noopener noreferrer" className="annotation font-semibold !text-[var(--ink)] inline-flex items-center gap-1 hover:!text-[var(--red)]">
                                        Original <ExternalLink size={11} aria-hidden />
                                    </a>
                                )}
                            </div>
                        </article>
                    );
                })}
            </div>
        </Reveal>
    );
}
