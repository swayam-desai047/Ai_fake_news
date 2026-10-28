import Link from 'next/link';
import { SECTIONS } from '@/lib/sections';

export default function SiteFooter() {
    return (
        <footer className="colophon no-print">
            <div className="np-container">
                <div className="grid gap-8 md:grid-cols-[1.3fr_1fr_1fr]">
                    <div>
                        <p className="font-[family-name:var(--font-display)] text-3xl font-black leading-none">The Daily Signal</p>
                        <p className="dek-sm mt-3 max-w-md">
                            An AI-assisted news intelligence platform. Credibility indicators, summaries and scores are
                            machine-generated aids for critical reading — they are not proof that a report is true or false.
                        </p>
                    </div>
                    <div>
                        <p className="kicker !text-[var(--ink)] mb-3">Sections</p>
                        <ul className="grid grid-cols-2 gap-x-4 gap-y-1.5 annotation">
                            {SECTIONS.map(s => (
                                <li key={s.slug}><Link className="hover:text-[var(--ink)]" href={`/section/${s.slug}`}>{s.label}</Link></li>
                            ))}
                        </ul>
                    </div>
                    <div>
                        <p className="kicker !text-[var(--ink)] mb-3">Intelligence</p>
                        <ul className="space-y-1.5 annotation">
                            <li><Link className="hover:text-[var(--ink)]" href="/compare">Cross-source coverage</Link></li>
                            <li><Link className="hover:text-[var(--ink)]" href="/analytics">The News Intelligence Report</Link></li>
                            <li><Link className="hover:text-[var(--ink)]" href="/search">Search the edition</Link></li>
                        </ul>
                    </div>
                </div>
                <hr className="rule mt-8 mb-4" />
                <p className="annotation text-center">
                    &copy; {new Date().getFullYear()} AK 0121 Agency · MIT-WPU M.Sc Computer Science, Group 17 — All rights reserved.
                    Headlines and excerpts belong to their original publishers and link to the source.
                </p>
            </div>
        </footer>
    );
}
