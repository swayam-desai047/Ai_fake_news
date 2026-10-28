'use client';

import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ExternalLink } from 'lucide-react';
import type { ExternalResult, ExternalSearchResponse } from '@/lib/externalSearch';
import { dateTime } from '@/lib/format';

type State =
    | { kind: 'idle' }
    | { kind: 'loading' }
    | { kind: 'done'; response: ExternalSearchResponse }
    | { kind: 'error'; message: string };

/**
 * "Beyond the edition": external news discovery for a search. Runs automatically when the local
 * edition has few matches, otherwise on request. Results are labelled as external and are only
 * linked to an analysis page when the provider supplied enough text to analyse.
 */
export default function ExternalResults({ q, since, autoRun }: { q: string; since?: string; autoRun: boolean }) {
    const [state, setState] = useState<State>({ kind: 'idle' });
    const started = useRef(false);

    const run = useCallback(async () => {
        setState({ kind: 'loading' });
        try {
            const res = await fetch(`/api/search/external?q=${encodeURIComponent(q)}&since=${encodeURIComponent(since || '')}`);
            const data = (await res.json()) as ExternalSearchResponse | { error: string };
            if ('error' in data) throw new Error(data.error);
            setState({ kind: 'done', response: data });
        } catch {
            setState({ kind: 'error', message: 'The external search service could not be reached from the server.' });
        }
    }, [q, since]);

    useEffect(() => {
        if (autoRun && !started.current) {
            started.current = true;
            void run();
        }
    }, [autoRun, run]);

    return (
        <section className="mt-12" aria-labelledby="ext-h" aria-live="polite" aria-busy={state.kind === 'loading'}>
            <div className="section-head">
                <h2 id="ext-h" className="section-head__title section-head__title--serif">Beyond the edition</h2>
                <span className="section-head__more">External news search</span>
            </div>
            <p className="annotation mt-2 max-w-3xl">
                Reports found by an external news search provider. They are not part of The Daily Signal&rsquo;s edition and are
                only analysed when the provider supplies enough of the publisher&rsquo;s text.
            </p>

            {state.kind === 'idle' && (
                <button type="button" className="btn btn--ghost mt-4" onClick={run}>Search other news sources</button>
            )}

            {state.kind === 'loading' && (
                <div className="mt-5 space-y-3" role="status">
                    <p className="dek-sm italic">Searching other news sources… this can take up to half a minute.</p>
                    {[0, 1, 2].map(i => <div key={i} className="skeleton h-14" />)}
                </div>
            )}

            {state.kind === 'error' && (
                <div className="notice mt-5" role="alert">
                    <p className="hl-3">External search unavailable</p>
                    <p className="dek-sm mt-1">{state.message} Results from the edition above are unaffected.</p>
                    <button type="button" className="btn btn--ghost mt-4" onClick={run}>Try again</button>
                </div>
            )}

            {state.kind === 'done' && <ExternalBody response={state.response} retry={run} />}
        </section>
    );
}

function ExternalBody({ response, retry }: { response: ExternalSearchResponse; retry: () => void }) {
    const providerNote = response.provider === 'Google News'
        ? 'Source: Live Global News API (real-time reports across original world publishers).'
        : response.provider === 'GDELT'
        ? 'Source: GDELT DOC 2.0 API.'
        : 'Source: GNews API.';

    if (response.status !== 'ok') {
        return (
            <div className="notice mt-5" role="alert">
                <p className="hl-3">{response.status === 'rate-limited' ? 'External search is busy' : 'External search unavailable'}</p>
                <p className="dek-sm mt-1">{response.message} Results from the edition above are unaffected.</p>
                {response.configHint && <p className="annotation mt-2">{response.configHint}</p>}
                <button type="button" className="btn btn--ghost mt-4" onClick={retry}>Try again</button>
            </div>
        );
    }

    if (response.results.length === 0) {
        return (
            <div className="mt-5 border-t border-[var(--rule)] pt-4">
                <p className="hl-3">No external reports matched every term.</p>
                <p className="annotation mt-1">{providerNote}</p>
            </div>
        );
    }

    return (
        <div className="mt-3">
            <p className="annotation">{response.results.length} external {response.results.length === 1 ? 'report' : 'reports'}. {providerNote}</p>
            <ol>
                {response.results.map(r => <ExternalRow key={r.id} result={r} />)}
            </ol>
        </div>
    );
}

function ExternalRow({ result: r }: { result: ExternalResult }) {
    return (
        <li className="grid gap-x-6 gap-y-2 py-5 border-b border-[var(--rule)] sm:grid-cols-[minmax(0,1fr)_160px]">
            <div className="min-w-0">
                <p className="flex flex-wrap items-baseline">
                    <span className="kicker !text-[var(--risk-verify)]">External · {r.provider}</span>
                    <span className="meta meta-sep">{r.publisher}</span>
                    {r.publishedAt && <time className="meta meta-sep" dateTime={r.publishedAt}>{dateTime(r.publishedAt)}</time>}
                </p>
                {r.analysed ? (
                    <Link href={`/article/${encodeURIComponent(r.id)}`} className="story-link mt-1.5"><h3 className="hl-2">{r.title}</h3></Link>
                ) : (
                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="story-link mt-1.5"><h3 className="hl-2">{r.title}</h3></a>
                )}
                {r.description && <p className="dek-sm mt-2 max-w-[68ch]">{r.description}</p>}
                <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1">
                    <span className={`risk ${r.analysed ? 'risk--low' : 'risk--verify'}`}>
                        <span className="risk__dot" aria-hidden />
                        {r.analysed ? 'Analysed from provider text' : 'Not analysed · headline only'}
                    </span>
                    {r.analysed && (
                        <Link href={`/article/${encodeURIComponent(r.id)}#analysis`} className="annotation font-semibold !text-[var(--ink)] hover:!text-[var(--red)]">
                            Analysis <span aria-hidden>→</span>
                        </Link>
                    )}
                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="annotation font-semibold !text-[var(--ink)] inline-flex items-center gap-1 hover:!text-[var(--red)]">
                        Original report <ExternalLink size={11} aria-hidden />
                    </a>
                </div>
            </div>
            {r.imageUrl && (
                // Provider images come from arbitrary publisher hosts.
                // eslint-disable-next-line @next/next/no-img-element
                <img src={r.imageUrl} alt="" loading="lazy" referrerPolicy="no-referrer" className="order-first sm:order-none w-full aspect-[3/2] object-cover bg-[var(--paper-2)]" />
            )}
        </li>
    );
}
