import type { DimensionKey } from './types';

export interface DimensionMeta {
    key: DimensionKey;
    label: string;
    short: string;
    /** What the ends of the 0–100 scale mean. Higher is not always "better". */
    low: string;
    high: string;
    /** For bipolar scales the middle (50) is the neutral point. */
    bipolar?: boolean;
}

export const DIMENSIONS: DimensionMeta[] = [
    { key: 'sentiment', label: 'Sentiment', short: 'Sentiment', low: 'negative tone', high: 'positive tone', bipolar: true },
    { key: 'bias', label: 'Bias', short: 'Bias', low: 'loaded / one-sided', high: 'balanced' },
    { key: 'objectivity', label: 'Objectivity', short: 'Objectivity', low: 'opinionated', high: 'factual' },
    { key: 'readability', label: 'Readability', short: 'Readability', low: 'dense', high: 'plain' },
    { key: 'propaganda', label: 'Propaganda / Manipulation', short: 'Manipulation', low: 'many markers', high: 'none detected' },
    { key: 'headline_accuracy', label: 'Headline Accuracy', short: 'Headline', low: 'unsupported', high: 'supported by text' },
    { key: 'source_credibility', label: 'Source Credibility', short: 'Source', low: 'unrated / weak', high: 'established' },
    { key: 'content_quality', label: 'Content Quality', short: 'Quality', low: 'thin', high: 'complete' },
];

export function dimensionMeta(key: DimensionKey): DimensionMeta {
    return DIMENSIONS.find(d => d.key === key)!;
}

export const METHOD_NOTE = {
    heuristic:
        'Scored by transparent lexical rules applied to the headline and the publisher’s feed excerpt: word lists for tone, subjectivity, loaded language and sensationalism; Flesch Reading Ease; headline-to-excerpt term overlap; and a hand-curated publisher reference table. No confidence value is reported because these rules are not a calibrated model.',
    model:
        'Scored by the backend pipeline: the BERT-tiny credibility classifier and the eight-dimension analyser, stored with the article at ingestion time.',
} as const;

export const DISCLAIMER =
    'These are AI-generated indicators for critical evaluation. They do not constitute proof that a report is true or false.';
