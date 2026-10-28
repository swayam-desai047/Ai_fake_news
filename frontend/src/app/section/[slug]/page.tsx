import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getEdition } from '@/lib/repository';
import { getSection } from '@/lib/sections';
import { delay } from '@/lib/motion';
import Reveal from '@/components/motion/Reveal';
import { ImageStory, MediaRowStory, TextStory } from '@/components/news/Stories';
import { SectionHeading } from '@/components/news/StoryParts';
import InfiniteFeed from '@/components/ui/InfiniteFeed';
import EditionUnavailable from '@/components/news/EditionUnavailable';

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const section = getSection((await params).slug);
    return { title: section?.heading ?? 'Section' };
}

const LIST_PAGE = 12;

export default async function SectionPage({ params }: Props) {
    const section = getSection((await params).slug);
    if (!section) notFound();

    const edition = await getEdition();
    const all = edition.articles.filter(a => a.section === section.slug);
    if (all.length === 0) {
        return <EditionUnavailable info={edition.info} message={`No ${section.label.toLowerCase()} reports are in the current edition.`} />;
    }

    const withImages = all.filter(a => a.imageUrl);
    const lead = withImages[0] ?? all[0];
    const rest = all.filter(a => a.id !== lead.id);
    const rail = rest.slice(0, 4);
    const grid = rest.slice(4).filter(a => a.imageUrl).slice(0, 6);
    const used = new Set([lead.id, ...rail.map(a => a.id), ...grid.map(a => a.id)]);
    const remaining = all.filter(a => !used.has(a.id));
    const briefs = remaining.slice(0, 4);
    const listing = remaining.slice(4);
    const publishers = [...new Set(all.map(a => a.publisher))];

    return (
        <div className="np-container pt-8">
            <header className="text-center">
                <p className="kicker enter">Section</p>
                <h1 className="italic-title text-[clamp(2.4rem,5vw,4rem)] leading-none mt-2 enter" style={delay(60)}>{section.heading}</h1>
                <p className="annotation mt-3 enter" style={delay(140)}>
                    {all.length} reports from {publishers.join(', ')}
                </p>
                <hr className="rule-double mt-5 enter-rule" style={delay(200)} />
            </header>

            <div className="layout-a pt-6">
                <div className="enter" style={delay(260)}>
                    <ImageStory article={lead} headline="hl-1" ratio="wide" summaryChars={420} />
                </div>
                <div className="mt-8 md:mt-0 enter" style={delay(340)}>
                    <p className="section-head__title border-b border-[var(--ink)] pb-2 mb-4">Also in {section.label}</p>
                    {rail.map((a, i) => (
                        <div key={a.id} className={i === 0 ? 'pb-4' : 'border-t border-[var(--rule)] py-4'}>
                            <MediaRowStory article={a} />
                        </div>
                    ))}
                </div>
            </div>

            {grid.length > 0 && (
                <Reveal as="section" className="mt-12" aria-labelledby="sec-photos">
                    <SectionHeading id="sec-photos" title={`${section.label} in pictures and words`} />
                    <div className="ruled-grid">
                        <div className="ruled-grid__inner cols-3">
                            {grid.map(a => (
                                <div key={a.id}><ImageStory article={a} headline="hl-3" summaryChars={220} /></div>
                            ))}
                        </div>
                    </div>
                </Reveal>
            )}

            {briefs.length > 0 && (
                <Reveal as="section" className="mt-12" aria-labelledby="sec-briefs">
                    <SectionHeading id="sec-briefs" title="In brief" serif />
                    <div className="ruled-grid">
                        <div className="ruled-grid__inner cols-4">
                            {briefs.map(a => (
                                <div key={a.id}><TextStory article={a} headline="hl-3" summaryChars={200} /></div>
                            ))}
                        </div>
                    </div>
                </Reveal>
            )}

            {listing.length > 0 && (
                <Reveal as="section" className="mt-12" aria-labelledby="sec-more">
                    <SectionHeading id="sec-more" title={`More ${section.label}`} />
                    <InfiniteFeed
                        initialArticles={listing.slice(0, LIST_PAGE)}
                        localPool={listing}
                        initialPage={1}
                        pageSize={LIST_PAGE}
                        hasMore={listing.length > LIST_PAGE}
                        showSection={false}
                    />
                </Reveal>
            )}
        </div>
    );
}
