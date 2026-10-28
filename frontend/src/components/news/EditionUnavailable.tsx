import Link from 'next/link';
import type { EditionInfo } from '@/lib/types';

/** Honest empty state when neither the database nor any publisher feed returned stories. */
export default function EditionUnavailable({ info, message }: { info?: EditionInfo | null; message?: string }) {
    return (
        <div className="np-container py-14">
            <div className="notice max-w-2xl mx-auto">
                <p className="kicker">Edition unavailable</p>
                <h1 className="hl-1 mt-3">The presses are quiet</h1>
                <p className="dek mt-4">
                    {message ?? 'No stories could be loaded. The ingestion database is not configured or is empty, and the publisher feeds did not respond.'}
                </p>
                {info && info.failedSources.length > 0 && (
                    <p className="annotation mt-4">Unreachable sources: {info.failedSources.join(', ')}.</p>
                )}
                <Link href="/" className="btn btn--ghost mt-6">Try again</Link>
            </div>
        </div>
    );
}
