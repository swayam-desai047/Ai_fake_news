import Link from 'next/link';
import { Search } from 'lucide-react';
import { editionDate, editionNumber, clockTime, EDITION_TZ_LABEL } from '@/lib/format';
import type { EditionInfo } from '@/lib/types';

interface MastheadProps {
    edition: EditionInfo | null;
}

/** Publication strip + nameplate. Rendered once per page, above the sticky section index. */
export default function Masthead({ edition }: MastheadProps) {
    const now = new Date();
    const { volume, issue } = editionNumber(now);
    const sourceLabel = edition?.origin === 'database' ? 'Ingestion database' : 'Live publisher feeds';

    return (
        <header>
            <div className="strip no-print">
                <div className="np-container strip__inner">
                    <div className="strip__group">
                        <span className="enter-fade" style={{ '--d': '0ms' } as React.CSSProperties}>{editionDate(now)}</span>
                        {edition && (
                            <span className="strip__live enter-fade hidden sm:inline-flex" style={{ '--d': '80ms' } as React.CSSProperties}>
                                Updated {clockTime(edition.fetchedAt)} {EDITION_TZ_LABEL}
                            </span>
                        )}
                    </div>
                    <div className="strip__group">
                        <span className="hidden md:inline">{sourceLabel}</span>
                        <Link href="/search" className="inline-flex items-center gap-1.5 font-semibold uppercase tracking-[0.1em] hover:text-[var(--ink)]">
                            <Search size={13} strokeWidth={2} aria-hidden />
                            <span>Search</span>
                        </Link>
                    </div>
                </div>
            </div>

            <div className="np-container">
                <hr className="rule-ink enter-rule" style={{ '--d': '60ms' } as React.CSSProperties} />
                <div className="masthead" data-masthead>
                    <Link href="/" aria-label="The Daily Signal — front page" className="inline-block">
                        <p className="nameplate enter" style={{ '--d': '120ms' } as React.CSSProperties}>The Daily Signal</p>
                    </Link>
                    <p className="masthead__tagline enter" style={{ '--d': '220ms' } as React.CSSProperties}>
                        News, context and credibility.
                    </p>
                    <div className="masthead__edition enter-fade" style={{ '--d': '300ms' } as React.CSSProperties}>
                        <span>Vol. {volume} · No. {issue}</span>
                        <span className="hide-sm">AI-assisted news intelligence</span>
                        <span>
                            {edition ? `${edition.articleCount} reports · ${edition.publisherCount} publishers` : 'Edition unavailable'}
                        </span>
                    </div>
                </div>
            </div>
        </header>
    );
}
