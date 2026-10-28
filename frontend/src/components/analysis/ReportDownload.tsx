'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';
import type { Article } from '@/lib/types';

/**
 * "Download PDF report". Database articles use the FastAPI ReportLab endpoint when the backend
 * URL is configured; every article can also be exported in the browser.
 */
export default function ReportDownload({ article, backendUrl }: { article: Article; backendUrl: string | null }) {
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const serverReport = backendUrl && article.origin === 'database'
        ? `${backendUrl.replace(/\/$/, '')}/api/v1/report/${encodeURIComponent(article.id)}`
        : null;

    const generate = async () => {
        setBusy(true);
        setError('');
        try {
            const { generateIntelligencePdf } = await import('@/lib/pdfReportGenerator');
            await generateIntelligencePdf(article);
        } catch {
            setError('The report could not be generated.');
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="space-y-2">
            {serverReport ? (
                <a href={serverReport} className="btn w-full" download>
                    <Download size={14} aria-hidden /> Download PDF report
                </a>
            ) : null}
            <button type="button" onClick={generate} disabled={busy} className={`btn w-full ${serverReport ? 'btn--ghost' : ''}`}>
                <Download size={14} aria-hidden /> {busy ? 'Typesetting report…' : serverReport ? 'Export in browser' : 'Download PDF report'}
            </button>
            {error && <p role="alert" className="annotation !text-[var(--red)]">{error}</p>}
        </div>
    );
}
