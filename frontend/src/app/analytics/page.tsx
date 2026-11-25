import type { Metadata } from 'next';
import Link from 'next/link';
import { getAnalytics } from '@/lib/repository';
import { sectionLabel } from '@/lib/sections';
import { DIMENSIONS, DISCLAIMER, METHOD_NOTE } from '@/lib/dimensions';
import { clockTime, dateTime, EDITION_TZ, EDITION_TZ_LABEL } from '@/lib/format';
import { delay } from '@/lib/motion';
import Reveal from '@/components/motion/Reveal';
import { HorizontalBars, Timeline } from '@/components/dashboard/DashboardAnalytics';
import EditionUnavailable from '@/components/news/EditionUnavailable';

export const metadata: Metadata = { title: 'The News Intelligence Report' };

const RISK_COLOR: Record<string, string> = {
    'Low Risk': '#1E6B3C',
    'Moderate Risk': '#8A5300',
    'High Risk': '#B32121',
    Unavailable: '#8A8883',
    'Needs Verification': '#3F4E63',
};

function Figure({ value, label, note }: { value: string | number; label: string; note?: string }) {
    return (
        <div className="py-4">
            <p className="figure-num">{value}</p>
            <p className="kicker !text-[var(--ink)] mt-2">{label}</p>
            {note && <p className="annotation mt-1">{note}</p>}
        </div>
    );
}

function Chart({ n, title, note, source, children }: { n: number; title: string; note: string; source: string; children: React.ReactNode }) {
    return (
        <div className="chart-block">
            <p className="annotation font-semibold uppercase tracking-[0.12em] !text-[0.62rem]">Figure {n}</p>
            <h3 className="chart-title mt-1">{title}</h3>
            <p className="chart-note">{note}</p>
            {children}
            <p className="chart-source">{source}</p>
        </div>
    );
}

export default async function AnalyticsPage() {
    const a = await getAnalytics();
    if (a.edition.articleCount === 0) return <EditionUnavailable info={a.edition} />;

    const total = a.edition.articleCount;
    const source = a.edition.origin === 'database'
        ? `Source: ingestion database, ${total} most recent reports.`
        : `Source: ${total} reports from live publisher feeds, fetched ${clockTime(a.edition.fetchedAt)} ${EDITION_TZ_LABEL}.`;
    const methods = a.analysisMethods.map(m => m.method);
    const verify = a.risk.find(r => r.label === 'Needs Verification')?.count ?? 0;
    const sentimentLabel: Record<string, string> = { negative: 'Negative', neutral: 'Neutral', positive: 'Positive', unscored: 'Not scored' };
    const hourFmt = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: EDITION_TZ });
    const dayFmt = new Intl.DateTimeFormat('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit', timeZone: EDITION_TZ });

    return (
        <div className="np-container pt-8">
            <header className="text-center max-w-3xl mx-auto">
                <p className="kicker enter">Research &amp; statistics</p>
                <h1 className="font-[family-name:var(--font-display)] font-black uppercase tracking-[0.02em] text-[clamp(1.9rem,4.6vw,3.4rem)] leading-[1.02] mt-2 enter" style={delay(60)}>
                    The News Intelligence Report
                </h1>
                <p className="dek mt-4 enter" style={delay(140)}>
                    What today&rsquo;s edition is made of: where the reports come from, how they were scored, and how often
                    the same event was covered by more than one newsroom.
                </p>
                <p className="annotation mt-3 enter" style={delay(200)}>As of {dateTime(a.edition.fetchedAt)}. {source}</p>
                <hr className="rule-double mt-6 enter-rule" style={delay(240)} />
            </header>

            <section aria-label="Headline figures" className="mt-2 ruled-grid">
                <div className="ruled-grid__inner cols-4 text-center">
                    <Figure value={total} label="Reports in the edition" note={`${a.edition.publisherCount} publishers`} />
                    <Figure value={a.coverage.groups} label="Events with multiple sources" note={`${a.coverage.articlesInGroups} reports grouped`} />
                    <Figure value={verify} label="Flagged for verification" note={`${Math.round((verify / total) * 100)}% of reports`} />
                    <Figure value={a.sections.length} label="Sections with news" note={a.sections.map(s => sectionLabel(s.section)).slice(0, 3).join(', ') + (a.sections.length > 3 ? '…' : '')} />
                </div>
            </section>

            <Reveal as="section" className="mt-10 border-t border-[var(--ink)] pt-6 grid gap-x-12 gap-y-12 lg:grid-cols-2" aria-label="Distribution charts">
                <Chart n={1} title="Where the edition’s reports sit" note="Number of reports per section." source={source}>
                    <HorizontalBars
                        ariaLabel={`Reports per section: ${a.sections.map(s => `${sectionLabel(s.section)} ${s.count}`).join(', ')}`}
                        data={a.sections.map(s => ({ label: sectionLabel(s.section), value: s.count }))}
                    />
                </Chart>

                <Chart
                    n={2}
                    title="Credibility-risk labels"
                    note="Risk labels are exclusive; “Needs verification” is a separate flag that can accompany any label (too little text, an ambiguous score, low classifier confidence, or the classifier and the rules disagreeing). “Not assessed” means no risk score could be computed."
                    source={`${source} Labels are indicators, not verdicts.`}
                >
                    <HorizontalBars
                        ariaLabel={`Risk labels: ${a.risk.map(r => `${r.label} ${r.count}`).join(', ')}`}
                        labelWidth={128}
                        data={a.risk.map(r => ({
                            label: r.label === 'Unavailable' ? 'Not assessed' : r.label,
                            value: r.count,
                            color: RISK_COLOR[r.label],
                            note: `${Math.round((r.count / total) * 100)}% of reports`,
                        }))}
                    />
                </Chart>

                <Chart n={3} title="Tone of coverage" note="Sentiment classification of each report’s headline and excerpt. Tone describes framing, not accuracy." source={source}>
                    <HorizontalBars
                        ariaLabel={`Sentiment: ${a.sentiment.map(s => `${sentimentLabel[s.sentiment]} ${s.count}`).join(', ')}`}
                        data={a.sentiment.map(s => ({ label: sentimentLabel[s.sentiment], value: s.count }))}
                    />
                </Chart>

                <Chart
                    n={4}
                    title="Average dimension scores"
                    note="Mean 0–100 score per dimension. Scales differ in direction: Sentiment centres on 50 (neutral), Readability is ease of reading, and the rest run from weak to strong."
                    source={`${source} Each average uses only the reports where that dimension could be scored (n in the tooltip).`}
                >
                    <HorizontalBars
                        ariaLabel={`Average scores: ${a.dimensionAverages.map(d => `${d.key} ${d.average ?? 'not scored'}`).join(', ')}`}
                        max={100}
                        labelWidth={150}
                        data={a.dimensionAverages.filter(d => d.average !== null).map(d => {
                            const meta = DIMENSIONS.find(m => m.key === d.key)!;
                            return { label: meta.label, value: d.average as number, note: `n = ${d.n} · 0 = ${meta.low} · 100 = ${meta.high}` };
                        })}
                    />
                </Chart>
            </Reveal>

            {a.timeline.length > 1 && (
                <Reveal as="section" className="mt-12 border-t border-[var(--ink)] pt-6" aria-label="Publication timeline">
                    <Chart
                        n={5}
                        title="When the reports were published"
                        note="Reports in the edition by hour of publication (last 36 hours). This reflects publishers’ timestamps, not the time they were fetched."
                        source={source}
                    >
                        <Timeline
                            ariaLabel="Reports published per hour over the last 36 hours"
                            data={a.timeline.map(t => ({
                                tick: hourFmt.format(new Date(t.hour)),
                                label: `${dayFmt.format(new Date(t.hour))} ${EDITION_TZ_LABEL}`,
                                count: t.count,
                            }))}
                        />
                    </Chart>
                </Reveal>
            )}

            <Reveal as="section" className="mt-12 border-t border-[var(--ink)] pt-6 grid gap-x-12 gap-y-12 lg:grid-cols-2" aria-label="Sources and coverage">
                <Chart n={6} title="Who supplied the reports" note="Reports per publisher in the edition." source={source}>
                    <HorizontalBars
                        ariaLabel={`Reports per publisher: ${a.publishers.map(p => `${p.publisher} ${p.count}`).join(', ')}`}
                        labelWidth={140}
                        data={a.publishers.slice(0, 10).map(p => ({ label: p.publisher, value: p.count }))}
                    />
                </Chart>

                <Chart
                    n={7}
                    title="How widely events were covered"
                    note={`Events grouped by the number of publishers reporting them. The widest-covered event drew ${a.coverage.largestGroup} publishers.`}
                    source={`${source} See Cross-source coverage for each event.`}
                >
                    {a.coverage.publishersPerGroup.length > 0 ? (
                        <HorizontalBars
                            ariaLabel={`Events by number of publishers: ${a.coverage.publishersPerGroup.map(p => `${p.publishers} publishers: ${p.groups} events`).join(', ')}`}
                            data={a.coverage.publishersPerGroup.map(p => ({ label: `${p.publishers} publishers`, value: p.groups, note: 'events' }))}
                        />
                    ) : (
                        <p className="dek-sm italic">No event is covered by more than one publisher yet.</p>
                    )}
                    <Link href="/compare" className="text-link mt-3 inline-block">Compare the coverage</Link>
                </Chart>
            </Reveal>

            <Reveal as="section" className="mt-12 border-t-[3px] border-double border-[var(--ink)] pt-5 max-w-3xl" aria-labelledby="method-h">
                <h2 id="method-h" className="italic-title text-xl">A note on method</h2>
                {methods.map(m => <p key={m} className="dek-sm mt-2">{METHOD_NOTE[m]}</p>)}
                <p className="dek-sm mt-2">{DISCLAIMER}</p>
            </Reveal>
        </div>
    );
}
