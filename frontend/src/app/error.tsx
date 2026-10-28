'use client';

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
    return (
        <div className="np-container py-16">
            <div className="notice max-w-2xl mx-auto">
                <p className="kicker">Stop the press</p>
                <h1 className="hl-1 mt-3">This page could not be set</h1>
                <p className="dek mt-4">Something went wrong while assembling the page. The news sources may be unreachable.</p>
                <button type="button" onClick={reset} className="btn btn--ghost mt-6">Try again</button>
            </div>
        </div>
    );
}
