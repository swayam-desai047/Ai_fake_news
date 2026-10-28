import Link from 'next/link';
import type { FrontSection } from '@/lib/frontPage';
import Reveal from '@/components/motion/Reveal';
import { articleHref, SectionHeading } from './StoryParts';
import { ImageStory, MediaRowStory, TextStory } from './Stories';

/**
 * A below-the-fold newspaper section. Four compositions rotate so consecutive sections have
 * their own rhythm:
 *  a — dominant photo story beside a rail of thumbnail headlines (7 : 5)
 *  b — text-only story index beside a pair of photo stories (4 : 8)
 *  c — lead photo story, two summarised stories, a headline list (5 : 4 : 3)
 *  d — ruled four-column photo grid over a row of text headlines
 */
export default function SectionBlock({ block }: { block: FrontSection }) {
    const { section, layout, articles } = block;
    const href = `/section/${section.slug}`;
    const [first, ...rest] = articles;
    if (!first) return null;

    return (
        <Reveal as="section" className="mt-14" aria-labelledby={`sec-${section.slug}`}>
            <SectionHeading id={`sec-${section.slug}`} title={section.heading} href={href} more={`All ${section.label}`} serif />

            {layout === 'a' && (
                <div className="layout-a pt-5">
                    <ImageStory article={first} headline="hl-1" ratio="wide" summaryChars={320} />
                    <div className="mt-6 md:mt-0">
                        {rest.slice(0, 4).map((a, i) => (
                            <div key={a.id} className={i === 0 ? 'pb-4' : 'border-t border-[var(--rule)] py-4'}>
                                <MediaRowStory article={a} />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {layout === 'b' && (
                <div className="layout-b pt-5">
                    <ol className="rail-list">
                        {articles.slice(2, 7).map(a => (
                            <li key={a.id} className="border-b border-[var(--rule)] py-3 first:pt-0 last:border-0">
                                <TextStory article={a} headline="hl-4" withSummary={false} />
                            </li>
                        ))}
                    </ol>
                    <div className="mt-6 md:mt-0 ruled-grid">
                        <div className="ruled-grid__inner cols-2">
                            {articles.slice(0, 2).map(a => (
                                <div key={a.id} className="!pt-0">
                                    <ImageStory article={a} headline="hl-2" summaryChars={260} />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {layout === 'c' && (
                <div className="layout-c pt-5">
                    <ImageStory article={first} headline="hl-2" summaryChars={260} />
                    <div className="mt-6 md:mt-0 space-y-5">
                        {rest.slice(0, 2).map((a, i) => (
                            <div key={a.id} className={i > 0 ? 'border-t border-[var(--rule)] pt-5' : ''}>
                                <TextStory article={a} headline="hl-2" summaryChars={240} />
                            </div>
                        ))}
                    </div>
                    <ul className="rail-list mt-6 md:mt-0">
                        {rest.slice(2, 6).map(a => (
                            <li key={a.id} className="border-b border-[var(--rule)] py-3 first:pt-0 last:border-0">
                                <Link href={articleHref(a)} className="story-link">
                                    <h3 className="hl-4">{a.title}</h3>
                                    <p className="meta mt-1 !text-[0.64rem]">{a.publisher}</p>
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {layout === 'd' && (
                <>
                    <div className="ruled-grid mt-1">
                        <div className="ruled-grid__inner cols-4">
                            {articles.slice(0, 4).map(a => (
                                <div key={a.id}>
                                    <ImageStory article={a} summaryChars={180} />
                                </div>
                            ))}
                        </div>
                    </div>
                    {articles.length > 4 && (
                        <div className="ruled-grid border-t border-[var(--rule)]">
                            <div className="ruled-grid__inner cols-4">
                                {articles.slice(4, 8).map(a => (
                                    <div key={a.id} className="!pt-4 !pb-4">
                                        <TextStory article={a} headline="hl-4" withSummary={false} />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </Reveal>
    );
}
