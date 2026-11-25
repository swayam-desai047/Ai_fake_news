import { describe, expect, it } from 'vitest';
import { analyseText, extractiveSummary, riskLabelFor } from './scoring';
import { clusterArticles } from './clustering';
import type { Article } from './types';

describe('analyseText', () => {
    it('is deterministic and never invents a confidence value', () => {
        const a = analyseText('Parliament passes budget', 'Lawmakers approved the budget on Tuesday, officials said, after a long debate over spending plans and taxes for the coming year.', 'BBC News');
        const b = analyseText('Parliament passes budget', 'Lawmakers approved the budget on Tuesday, officials said, after a long debate over spending plans and taxes for the coming year.', 'BBC News');
        expect(a).toEqual(b);
        expect(a.credibility.confidence).toBeNull();
    });

    it('keeps every dimension within 0–100 and explains each one', () => {
        const r = analyseText('SHOCKING!!! You won’t believe this secret', 'Exposed.', 'Unknown Blog');
        for (const [k, v] of Object.entries(r.dimensions)) {
            if (k === 'explanations' || v === null) continue;
            expect(v).toBeGreaterThanOrEqual(0);
            expect(v).toBeLessThanOrEqual(100);
        }
        expect(Object.keys(r.dimensions.explanations)).toHaveLength(8);
        expect(r.dimensions.propaganda).toBeLessThan(50);
    });

    it('flags short excerpts as needing verification (handover: under 150 characters)', () => {
        expect(analyseText('Headline', 'Too short to judge.', 'BBC News').credibility.needsVerification).toBe(true);
    });

    it('never gives a headline-only article from an unknown publisher a risk label', () => {
        const r = analyseText('Markets fall sharply', '', 'Unknown Blog');
        expect(r.credibility.label).toBe('Unavailable');
        expect(r.credibility.score).toBeNull();
        expect(r.credibility.needsVerification).toBe(true);
        expect(r.dimensions.headline_accuracy).toBeNull();
        expect(r.dimensions.source_credibility).toBeNull();
        expect(r.dimensions.explanations.headline_accuracy).toMatch(/^Not scored/);
    });

    it('does not assign a source score to publishers outside the reference table', () => {
        const r = analyseText('Council approves park', 'The city council voted to approve a new park, a spokesperson said on Monday evening after a long meeting with residents.', 'Local Gazette');
        expect(r.dimensions.source_credibility).toBeNull();
        expect(r.credibility.score).not.toBeNull();
    });

    it('maps risk scores onto the handover thresholds', () => {
        expect(riskLabelFor(0.35)).toBe('Low Risk');
        expect(riskLabelFor(0.36)).toBe('Moderate Risk');
        expect(riskLabelFor(0.66)).toBe('High Risk');
    });

    it('only produces an extractive summary when there is enough text to condense', () => {
        expect(extractiveSummary('One sentence only.')).toBeNull();
        expect(extractiveSummary('First sentence is long enough to count here. Second sentence is also long enough. Third sentence is long enough as well.'))
            .toBe('First sentence is long enough to count here. Second sentence is also long enough.');
    });
});

describe('clusterArticles', () => {
    const make = (id: string, publisher: string, title: string): Article => ({
        id, title, publisher, sourceUrl: null, imageUrl: null, excerpt: '', summary: null, summaryKind: null,
        section: 'world', author: null, publishedAt: new Date().toISOString(), ingestedAt: null, sentiment: null,
        credibility: { label: 'Low Risk', score: 0.1, confidence: null, needsVerification: false, reasoning: null },
        dimensions: null, groupId: null, eventTitle: null, origin: 'live-feed', analysisMethod: 'heuristic',
    });

    it('groups the same event across publishers and ignores unrelated stories', () => {
        const groups = clusterArticles([
            make('1', 'BBC News', 'Netherlands pulls out of Eurovision over Israel participation'),
            make('2', 'Al Jazeera', 'The Netherlands pulls out of Eurovision 2027 due to Israel sensitivities'),
            make('3', 'The Hindu', 'Monsoon rains flood Chennai streets'),
        ]);
        expect(groups).toHaveLength(1);
        expect(groups[0].publishers.sort()).toEqual(['Al Jazeera', 'BBC News']);
    });

    it('does not group two reports from the same publisher', () => {
        const groups = clusterArticles([
            make('1', 'BBC News', 'Netherlands pulls out of Eurovision over Israel'),
            make('2', 'BBC News', 'Netherlands pulls out of Eurovision over Israel row'),
        ]);
        expect(groups).toHaveLength(0);
    });
});
