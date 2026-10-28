import { describe, expect, it, vi } from 'vitest';
import { generateIntelligencePdf } from './pdfReportGenerator';
import { analyseText } from './scoring';
import type { Article } from './types';

const recorded = vi.hoisted(() => ({ saved: [] as string[], text: [] as string[], pages: 0 }));

vi.mock('jspdf', async importOriginal => {
    const real = await importOriginal<typeof import('jspdf')>();
    class RecordingPdf extends real.jsPDF {
        constructor(...args: ConstructorParameters<typeof real.jsPDF>) {
            super(...args);
            const text = this.text.bind(this);
            this.text = ((value: string | string[], ...rest: unknown[]) => {
                recorded.text.push(Array.isArray(value) ? value.join(' ') : value);
                return (text as (...a: unknown[]) => unknown)(value, ...rest);
            }) as typeof this.text;
            this.save = ((name: string) => {
                recorded.saved.push(name);
                recorded.pages = this.getNumberOfPages();
                return this;
            }) as unknown as typeof this.save;
        }
    }
    return { ...real, jsPDF: RecordingPdf };
});

describe('generateIntelligencePdf', () => {
    it('builds the report and states missing confidence instead of inventing it', async () => {
        const excerpt = 'Shares rose on Tuesday, analysts said, as investors welcomed the results.';
        const analysis = analyseText('Markets rise after ₹ rally', excerpt, 'Mint');
        const article: Article = {
            id: 'lv-x', title: 'Markets rise after ₹ rally', publisher: 'Mint', sourceUrl: 'https://www.livemint.com/x',
            imageUrl: null, excerpt, summary: null, summaryKind: null, section: 'business', author: null,
            publishedAt: '2026-10-27T10:00:00Z', ingestedAt: null, sentiment: analysis.sentiment,
            credibility: analysis.credibility, dimensions: analysis.dimensions,
            groupId: null, eventTitle: null, origin: 'live-feed', analysisMethod: 'heuristic',
        };

        await generateIntelligencePdf(article);

        expect(recorded.saved).toEqual([expect.stringMatching(/^daily-signal-report-markets-rise/)]);
        expect(recorded.pages).toBeGreaterThanOrEqual(1);
        const printed = recorded.text.join(' ');
        expect(printed).toContain('Not reported');
        expect(printed).toContain('Headline Accuracy');
        expect(printed).toContain('Rs rally');
    });
});
