import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ExternalLink } from 'lucide-react';
import { getArticle, relatedArticles } from '@/lib/repository';
import { getSection, sectionLabel } from '@/lib/sections';
import { dateTime, pct } from '@/lib/format';
import { delay } from '@/lib/motion';
import { DISCLAIMER, METHOD_NOTE } from '@/lib/dimensions';
import { DIMENSION_KEYS, type DimensionKey } from '@/lib/types';
import StoryImage from '@/components/news/StoryImage';
import { articleHref, paragraphs, RiskMark, SectionHeading } from '@/components/news/StoryParts';
import { ImageStory } from '@/components/news/Stories';
import Reveal from '@/components/motion/Reveal';
import DimensionRadarChart from '@/components/ui/DimensionRadarChart';
import DimensionTable from '@/components/analysis/DimensionTable';
import ReportDownload from '@/components/analysis/ReportDownload';

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const found = await getArticle(decodeURIComponent((await params).id));
    return { title: found?.article.title ?? 'Article not found' };
}

export default async function ArticlePage({ params }: Props) {
    const found = await getArticle(decodeURIComponent((await params).id));
    if (!found) notFound();
    const { article, edition } = found;
    const section = getSection(article.section) ?? { slug: 'world' as const, label: 'World', heading: 'World News', feeds: [] };
    const excerptParas = paragraphs(article.excerpt);
    const group = article.groupId ? edition.groups.find(g => g.groupId === article.groupId) : undefined;
    const others = group?.articles.filter(a => a.id !== article.id) ?? [];
    const related = relatedArticles(edition, article, 4);
    const c = article.credibility;

    const scored = edition.articles.filter(a => a.dimensions && a.analysisMethod === article.analysisMethod);
    const average = scored.length > 5
        ? Object.fromEntries(DIMENSION_KEYS.map(k => [k, Math.round(scored.reduce((s, a) => s + a.dimensions![k], 0) / scored.length)])) as Record<DimensionKey, number>
        : null;

    const standfirst = article.summaryKind === 'ai' ? article.summary : null;

    return (
        <article className="np-container pt-6">
            <nav aria-label="Breadcrumb" className="enter">
                <ol className="breadcrumb flex flex-wrap">
                    <li><Link href="/">Front page</Link></li>
                    <li><Link href={`/section/${section.slug}`}>{section.label}</Link></li>
                    <li aria-current="page" className="text-[var(--ink)]">{article.publisher}</li>
                </ol>
            </nav>

            <header className="mt-6 max-w-[920px]">
                <p className="kicker enter" style={delay(60)}>{sectionLabel(article.section)}</p>
                <h1 className="hl-lead !text-[clamp(2rem,4.2vw,3.6rem)] mt-3 enter" style={delay(120)}>{article.title}</h1>
                {standfirst && <p className="dek !text-[1.2rem] mt-4 enter" style={delay(200)}>{standfirst}</p>}
                <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 border-y border-[var(--rule)] py-3 enter" style={delay(260)}>
                    <p className="meta !text-[var(--ink)]">
                        {article.author ? <>By <strong>{article.author}</strong> · </> : null}
                        <strong>{article.publisher}</strong>
                    </p>
                    <p className="meta"><time dateTime={article.publishedAt ?? undefined}>{dateTime(article.publishedAt)}</time></p>
                    <RiskMark credibility={c} />
                    {article.sourceUrl && (
                        <a href={article.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-link inline-flex items-center gap-1.5 ml-auto">
                            Original report <ExternalLink size={12} aria-hidden />
                        </a>
                    )}
                </div>
            </header>

            {article.imageUrl && (
                <StoryImage article={article} ratio="wide" priority credit className="mt-6 max-w-[1100px] enter-img" style={delay(320)} />
            )}

            <div className="article-grid mt-8">
                <div className="reading">
                    <section className="provenance" aria-labelledby="prov-h">
                        <p id="prov-h" className="provenance__label">
                            {article.origin === 'live-feed'
                                ? 'Publisher’s excerpt · supplied by RSS feed'
                                : article.origin === 'external'
                                    ? 'External search result · description supplied by the news search provider'
                                    : 'Stored excerpt · ingestion database'}
                        </p>
                        <p className="annotation mt-1">
                            The Daily Signal does not reproduce full articles. The complete report is published by {article.publisher}.
                        </p>
                    </section>

                    <div className="body-copy mt-6">
                        {excerptParas.length > 0 ? (
                            excerptParas.map((p, i) => (
                                <p key={i} className={`justify ${i === 0 && p.length > 120 ? 'dropcap' : ''}`}>{p}</p>
                            ))
                        ) : (
                            <p className="italic text-[var(--ink-2)]">The publisher&rsquo;s feed supplied a headline only.</p>
                        )}
                    </div>

                    {article.sourceUrl && (
                        <a href={article.sourceUrl} target="_blank" rel="noopener noreferrer" className="btn mt-2">
                            Continue reading at {article.publisher} <ExternalLink size={13} aria-hidden />
                        </a>
                    )}

                    {article.summary && article.summaryKind && (
                        <section className="mt-10 border-t-2 border-[var(--ink)] pt-4" aria-labelledby="sum-h">
                            <h2 id="sum-h" className="provenance__label">
                                {article.summaryKind === 'ai' ? 'AI executive summary' : 'Extractive summary — sentences selected from the excerpt'}
                            </h2>
                            <p className="dek mt-2 italic">{article.summary}</p>
                        </section>
                    )}
                </div>

                <aside className="mt-12 lg:mt-0 space-y-8" aria-label="Credibility and coverage">
                    <section aria-labelledby="cred-h">
                        <h2 id="cred-h" className="section-head__title border-b border-[var(--ink)] pb-2">Credibility</h2>
                        <dl className="mt-3 divide-y divide-[var(--rule)]">
                            <div className="flex justify-between gap-4 py-2"><dt className="annotation">Risk label</dt><dd><RiskMark credibility={{ ...c, needsVerification: false }} /></dd></div>
                            <div className="flex justify-between gap-4 py-2"><dt className="annotation">Risk score</dt><dd className="font-semibold">{c.score !== null ? c.score.toFixed(2) : '—'}</dd></div>
                            <div className="flex justify-between gap-4 py-2"><dt className="annotation">Model confidence</dt><dd className="font-semibold">{c.confidence !== null ? pct(c.confidence) : 'Not reported'}</dd></div>
                            <div className="flex justify-between gap-4 py-2"><dt className="annotation">Verification</dt><dd className={`font-semibold ${c.needsVerification ? 'text-[var(--risk-verify)]' : ''}`}>{c.needsVerification ? 'Needs verification' : 'Not flagged'}</dd></div>
                        </dl>
                        {c.reasoning && <p className="dek-sm mt-3 italic">{c.reasoning}</p>}
                        <p className="annotation mt-3">Risk score runs 0–1 and is not a calibrated probability. {DISCLAIMER}</p>
                        <div className="mt-4 no-print">
                            <ReportDownload article={article} backendUrl={process.env.NEXT_PUBLIC_API_URL ?? null} />
                            <Link href="#analysis" className="text-link mt-4 inline-block">Read the analysis supplement</Link>
                        </div>
                    </section>

                    {others.length > 0 && group && (
                        <section aria-labelledby="cov-h">
                            <h2 id="cov-h" className="section-head__title border-b border-[var(--ink)] pb-2">Also reported by</h2>
                            <ul>
                                {others.map(o => (
                                    <li key={o.id} className="border-b border-[var(--rule)] py-3">
                                        <p className="meta !text-[var(--ink)] font-bold">{o.publisher}</p>
                                        <Link href={articleHref(o)} className="story-link mt-1"><h3 className="hl-4 italic !font-normal">&ldquo;{o.title}&rdquo;</h3></Link>
                                    </li>
                                ))}
                            </ul>
                            <Link href={`/compare#${group.groupId}`} className="text-link mt-3 inline-block">Compare the coverage</Link>
                        </section>
                    )}
                </aside>
            </div>

            {/* ── Analysis supplement ───────────────────────────────────────────── */}
            <Reveal as="section" id="analysis" className="supplement mt-14 scroll-mt-16" aria-labelledby="analysis-h">
                <div className="px-0 sm:px-6">
                    <p className="kicker">Research supplement</p>
                    <h2 id="analysis-h" className="italic-title text-[clamp(1.7rem,3vw,2.5rem)] leading-tight mt-1">The Analysis</h2>
                    <p className="dek-sm mt-2 max-w-3xl">{METHOD_NOTE[article.analysisMethod]}</p>
                    {article.dimensions ? (
                        <div className="mt-6 grid gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
                            <div>
                                <h3 className="chart-title">Eight-dimension profile</h3>
                                <p className="chart-note">Each axis runs 0–100. Higher is not always better: read each scale&rsquo;s labels in the table.</p>
                                <DimensionRadarChart dimensions={article.dimensions} comparison={average} />
                                {average && <p className="chart-source">Edition average across {scored.length} reports scored the same way.</p>}
                            </div>
                            <DimensionTable dimensions={article.dimensions} />
                        </div>
                    ) : (
                        <p className="dek mt-6 italic">No dimension scores are recorded for this article yet.</p>
                    )}
                    <p className="annotation mt-6 border-t border-[var(--ink)] pt-3">{DISCLAIMER}</p>
                </div>
            </Reveal>

            {related.length > 0 && (
                <Reveal as="section" className="mt-14" aria-labelledby="rel-h">
                    <SectionHeading id="rel-h" title={`More from ${section.label}`} href={`/section/${section.slug}`} />
                    <div className="ruled-grid">
                        <div className="ruled-grid__inner cols-4">
                            {related.map(a => <div key={a.id}><ImageStory article={a} summaryChars={160} /></div>)}
                        </div>
                    </div>
                </Reveal>
            )}
        </article>
    );
}
