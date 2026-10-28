import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getEdition } from '@/lib/repository';
import { composeFrontPage } from '@/lib/frontPage';
import { getSection } from '@/lib/sections';
import { delay } from '@/lib/motion';
import { timeAgo } from '@/lib/format';
import Reveal from '@/components/motion/Reveal';
import SectionBlock from '@/components/news/SectionBlock';
import { FeedItem, ImageStory, LeadStory, RailItem } from '@/components/news/Stories';
import { articleHref, SectionHeading } from '@/components/news/StoryParts';
import EditionUnavailable from '@/components/news/EditionUnavailable';

export const dynamic = 'force-dynamic';

export default async function Home(props: {
  searchParams?: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  // Links from the previous single-page dashboard keep working.
  const sp = (await props.searchParams) || {};
  const one = (k: string) => (typeof sp[k] === 'string' ? (sp[k] as string) : '');
  if (one('view').toLowerCase() === 'comparison') redirect('/compare');
  if (one('q') || one('risk')) {
    const params = new URLSearchParams();
    if (one('q')) params.set('q', one('q'));
    if (one('category') && getSection(one('category'))) params.set('section', one('category').toLowerCase());
    const risk = one('risk').toLowerCase();
    if (risk === 'fake') params.set('risk', 'High Risk');
    if (risk === 'low') params.set('risk', 'Low Risk');
    if (risk === 'verification') params.set('verify', '1');
    redirect(`/search?${params.toString()}`);
  }
  if (getSection(one('category'))) redirect(`/section/${one('category').toLowerCase()}`);

  const edition = await getEdition();
  if (edition.articles.length === 0) {
    return <EditionUnavailable info={edition.info} />;
  }

  const front = composeFrontPage(edition);
  const { lead, leadGroup } = front;
  const counts = {
    low: edition.articles.filter(a => a.credibility.label === 'Low Risk').length,
    moderate: edition.articles.filter(a => a.credibility.label === 'Moderate Risk').length,
    high: edition.articles.filter(a => a.credibility.label === 'High Risk').length,
    verify: edition.articles.filter(a => a.credibility.needsVerification).length,
  };

  return (
    <div className="np-container pt-6" suppressHydrationWarning>
      {/* ── Front page: Latest | Breaking | Daily feed ─────────────────────── */}
      <div className="front">
        <section className="front__latest enter" style={delay(560)} aria-labelledby="latest-h">
          <SectionHeading id="latest-h" title="Latest Articles" />
          <ol className="rail-list">
            {front.latest.map(a => <RailItem key={a.id} article={a} />)}
          </ol>
          <Link href="/search?sort=newest" className="text-link mt-3 inline-block">View all articles</Link>
        </section>

        <section className="front__lead" aria-labelledby="breaking-h">
          <div className="enter" style={delay(380)}>
            <SectionHeading id="breaking-h" title="Breaking News">
              {lead?.publishedAt && <span className="section-head__more !text-[var(--red)]">{timeAgo(lead.publishedAt)}</span>}
            </SectionHeading>
          </div>
          <div className="pt-5">
            {lead && <LeadStory article={lead} />}
            {leadGroup && leadGroup.articles.length > 1 && (
              <div className="mt-5 border-t border-[var(--ink)] pt-3 enter" style={delay(720)}>
                <p className="kicker !text-[var(--ink)]">Also reporting this story</p>
                <ul className="mt-2 space-y-2">
                  {leadGroup.articles.filter(a => a.id !== lead?.id).map(a => (
                    <li key={a.id} className="dek-sm">
                      <span className="meta !text-[var(--ink)] font-semibold">{a.publisher}</span>{' '}
                      <Link href={articleHref(a)} className="inline-link italic">{a.title}</Link>
                    </li>
                  ))}
                </ul>
                <Link href={`/compare#${leadGroup.groupId}`} className="text-link mt-3 inline-block">
                  Compare {leadGroup.publishers.length} publishers&rsquo; coverage
                </Link>
              </div>
            )}
          </div>

          {front.supporting.length > 0 && (
            <div className="ruled-grid mt-7 border-t border-[var(--ink)] enter" style={delay(800)}>
              <div className="ruled-grid__inner supporting">
                {front.supporting.map(a => (
                  <div key={a.id}>
                    <ImageStory article={a} headline="hl-3" summaryChars={140} showRisk={false} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="front__feed enter" style={delay(640)} aria-labelledby="feed-h">
          <SectionHeading id="feed-h" title="Daily Feed" />
          <div>
            {front.daily.map(a => <FeedItem key={a.id} article={a} />)}
          </div>
        </section>
      </div>

      {/* ── Edition at a glance ─────────────────────────────────────────────── */}
      <Reveal as="aside" className="mt-12 border-y border-[var(--ink)] py-3" aria-label="Edition credibility at a glance">
        <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-2">
          <p className="italic-title text-lg">The edition at a glance</p>
          <dl className="flex flex-wrap gap-x-7 gap-y-1 annotation">
            <div className="flex gap-2"><dt>Reports</dt><dd className="font-semibold !text-[var(--ink)]">{edition.articles.length}</dd></div>
            <div className="flex gap-2"><dt className="risk risk--low"><span className="risk__dot" />Low</dt><dd className="font-semibold !text-[var(--ink)]">{counts.low}</dd></div>
            <div className="flex gap-2"><dt className="risk risk--moderate"><span className="risk__dot" />Moderate</dt><dd className="font-semibold !text-[var(--ink)]">{counts.moderate}</dd></div>
            <div className="flex gap-2"><dt className="risk risk--high"><span className="risk__dot" />High</dt><dd className="font-semibold !text-[var(--ink)]">{counts.high}</dd></div>
            <div className="flex gap-2"><dt className="risk risk--verify"><span className="risk__dot" />Needs verification</dt><dd className="font-semibold !text-[var(--ink)]">{counts.verify}</dd></div>
          </dl>
          <Link href="/analytics" className="text-link">Read the intelligence report</Link>
        </div>
      </Reveal>

      {/* ── Featured stories ────────────────────────────────────────────────── */}
      {front.featured.length > 0 && (
        <Reveal as="section" className="mt-12" aria-labelledby="featured-h">
          <SectionHeading id="featured-h" title="Featured Stories" />
          <div className="ruled-grid">
            <div className="ruled-grid__inner cols-4">
              {front.featured.map(a => (
                <div key={a.id}>
                  <ImageStory article={a} headline="hl-3" summaryChars={200} />
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      )}

      {/* ── Most-covered events ─────────────────────────────────────────────── */}
      {front.mostCovered.length > 0 && (
        <Reveal as="section" className="mt-14" aria-labelledby="covered-h">
          <SectionHeading id="covered-h" title="Most-Covered Events" href="/compare" more="Compare coverage" serif />
          <div className="ruled-grid" suppressHydrationWarning>
            <div className="ruled-grid__inner cols-3">
              {front.mostCovered.map(g => (
                <article key={g.groupId}>
                  <p className="kicker">{g.publishers.length} publishers</p>
                  <h3 className="hl-2 mt-1.5">
                    <Link href={`/compare#${g.groupId}`} className="headline-link">{g.eventTitle}</Link>
                  </h3>
                  <ul className="mt-3">
                    {g.articles.map(a => (
                      <li key={a.id} className="border-t border-[var(--rule)] py-2">
                        <p className="meta !text-[0.62rem] !text-[var(--ink)] font-bold">{a.publisher}</p>
                        <Link href={articleHref(a)} className="dek-sm italic block mt-0.5 hover:text-[var(--ink)]">&ldquo;{a.title}&rdquo;</Link>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </Reveal>
      )}

      {/* ── Sections ────────────────────────────────────────────────────────── */}
      {front.sections.map(block => <SectionBlock key={block.section.slug} block={block} />)}
    </div>
  );
}
