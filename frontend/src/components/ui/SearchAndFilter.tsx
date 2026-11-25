import Link from 'next/link';
import { SECTIONS } from '@/lib/sections';
import type { ArticleQuery } from '@/lib/types';

interface SearchAndFilterProps {
    query: ArticleQuery;
    publishers: string[];
}

/**
 * Search form for the edition. A plain GET form, so it works with or without JavaScript and every
 * result page is a shareable URL.
 */
export default function SearchAndFilter({ query, publishers }: SearchAndFilterProps) {
    const active = Boolean(query.q || query.section || query.publisher || query.risk || query.needsVerification || query.sort || query.since);
    return (
        <form action="/search" method="get" role="search" className="border-b border-[var(--ink)] pb-6">
            <label htmlFor="q" className="field-label">Search headlines and text</label>
            <div className="flex items-end gap-4">
                <input
                    id="q"
                    name="q"
                    type="search"
                    defaultValue={query.q}
                    placeholder="Search the edition…"
                    className="field field--search flex-1 min-w-0"
                    autoComplete="off"
                    enterKeyHint="search"
                />
                <button type="submit" className="btn shrink-0">Search</button>
            </div>

            <fieldset className="mt-6 grid gap-x-6 gap-y-5 sm:grid-cols-2 lg:grid-cols-[repeat(5,minmax(0,1fr))_auto]">
                <legend className="sr-only">Filters</legend>
                <div>
                    <label htmlFor="section" className="field-label">Section</label>
                    <select id="section" name="section" defaultValue={query.section || ''} className="field">
                        <option value="">All sections</option>
                        {SECTIONS.map(s => <option key={s.slug} value={s.slug}>{s.label}</option>)}
                    </select>
                </div>
                <div>
                    <label htmlFor="publisher" className="field-label">Publisher</label>
                    <select id="publisher" name="publisher" defaultValue={query.publisher || ''} className="field">
                        <option value="">All publishers</option>
                        {publishers.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                </div>
                <div>
                    <label htmlFor="risk" className="field-label">Credibility risk</label>
                    <select id="risk" name="risk" defaultValue={query.risk || ''} className="field">
                        <option value="">Any risk level</option>
                        <option value="Low Risk">Low risk</option>
                        <option value="Moderate Risk">Moderate risk</option>
                        <option value="High Risk">High risk</option>
                        <option value="Unavailable">Not assessed</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="sort" className="field-label">Order</label>
                    <select id="sort" name="sort" defaultValue={query.sort || ''} className="field">
                        <option value="">Best match</option>
                        <option value="newest">Newest first</option>
                        <option value="oldest">Oldest first</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="since" className="field-label">Published</label>
                    <select id="since" name="since" defaultValue={query.since || ''} className="field">
                        <option value="">Any time</option>
                        <option value="24h">Last 24 hours</option>
                        <option value="7d">Last 7 days</option>
                        <option value="30d">Last 30 days</option>
                    </select>
                </div>
                <div className="flex items-end gap-5 pb-1.5">
                    <label className="checkbox whitespace-nowrap">
                        <input type="checkbox" name="verify" value="1" defaultChecked={query.needsVerification} />
                        Needs verification only
                    </label>
                </div>
            </fieldset>
            <div className="mt-5 flex items-center gap-5">
                <button type="submit" className="btn btn--ghost">Apply filters</button>
                {active && <Link href="/search" className="text-link">Clear filters</Link>}
            </div>
        </form>
    );
}
