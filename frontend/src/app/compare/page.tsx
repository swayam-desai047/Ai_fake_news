import type { Metadata } from 'next';
import Link from 'next/link';
import { getGroups } from '@/lib/repository';
import { SIMILARITY_THRESHOLD } from '@/lib/clustering';
import { delay } from '@/lib/motion';
import CrossSourceView from '@/components/dashboard/CrossSourceView';

export const metadata: Metadata = { title: 'Cross-Source Coverage' };

export default async function ComparePage() {
    const { groups, info } = await getGroups();
    const method = info.origin === 'database' && groups.some(g => !g.groupId.startsWith('ev-'))
        ? 'Groups come from the backend clustering service (stored group_id).'
        : `Reports are matched by TF-IDF cosine similarity of headline and lead sentence (threshold ${SIMILARITY_THRESHOLD}), within a 48-hour window, and a group needs at least two different publishers.`;

    return (
        <div className="np-container pt-8">
            <header className="text-center max-w-3xl mx-auto">
                <p className="kicker enter">Cross-source coverage</p>
                <h1 className="italic-title text-[clamp(2.3rem,5vw,3.8rem)] leading-[1.02] mt-2 enter" style={delay(60)}>
                    One story, many newsrooms
                </h1>
                <p className="dek mt-4 enter" style={delay(140)}>
                    The same event, as different publishers chose to headline and frame it. Differences in emphasis or
                    tone are normal editorial judgement — they do not by themselves indicate misinformation.
                </p>
                <p className="annotation mt-3 enter" style={delay(200)}>{method}</p>
                <hr className="rule-double mt-6 enter-rule" style={delay(240)} />
            </header>

            {groups.length === 0 ? (
                <div className="notice mt-10 max-w-2xl mx-auto">
                    <h2 className="hl-2">No shared stories in this edition yet</h2>
                    <p className="dek-sm mt-2">
                        No event is currently covered by two or more publishers in the edition. Groups appear automatically as
                        outlets report the same story.
                    </p>
                    <Link href="/" className="btn btn--ghost mt-5">Back to the front page</Link>
                </div>
            ) : (
                <>
                    <nav aria-label="Events in this edition" className="mt-6">
                        <p className="section-head__title border-b border-[var(--ink)] pb-2">{groups.length} events covered by more than one publisher</p>
                        <ol className="mt-3 grid gap-x-8 gap-y-2 sm:grid-cols-2 lg:grid-cols-3 list-decimal list-inside">
                            {groups.map(g => (
                                <li key={g.groupId} className="dek-sm marker:font-semibold marker:text-[var(--ink-2)]">
                                    <Link href={`#${g.groupId}`} className="inline-link">{g.eventTitle}</Link>
                                    <span className="annotation"> · {g.publishers.length}</span>
                                </li>
                            ))}
                        </ol>
                    </nav>
                    {groups.map((g, i) => <CrossSourceView key={g.groupId} group={g} index={i} />)}
                </>
            )}
        </div>
    );
}
