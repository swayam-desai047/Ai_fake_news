/**
 * Canonical data shapes used across the publication.
 *
 * Every article — whether it came from the Supabase `articles` table (written by the
 * FastAPI ingestion pipeline) or straight from a publisher's live RSS feed — is normalised
 * into `Article` before it reaches a component.
 */

export type SectionSlug =
    | 'world'
    | 'india'
    | 'politics'
    | 'business'
    | 'technology'
    | 'science'
    | 'culture'
    | 'sports';

export type RiskLabel = 'Low Risk' | 'Moderate Risk' | 'High Risk';
export type Sentiment = 'positive' | 'negative' | 'neutral';

export const DIMENSION_KEYS = [
    'sentiment',
    'bias',
    'objectivity',
    'readability',
    'propaganda',
    'headline_accuracy',
    'source_credibility',
    'content_quality',
] as const;

export type DimensionKey = (typeof DIMENSION_KEYS)[number];

export type DimensionScores = Record<DimensionKey, number> & {
    explanations: Partial<Record<DimensionKey, string>>;
};

/** Where an article's record lives, which decides what can be done with it (e.g. server PDF reports). */
/** `external`: found through external news search (GNews), analysed from the provider's text. */
export type ArticleOrigin = 'database' | 'live-feed' | 'external';

/**
 * How the credibility indicators were produced.
 *  - `model`: the backend's BERT-tiny classifier + dimension engine (stored in Supabase).
 *  - `heuristic`: the frontend's transparent lexical rules, applied to live feed excerpts.
 */
export type AnalysisMethod = 'model' | 'heuristic';

export interface CredibilityAssessment {
    label: RiskLabel;
    /** 0 (no risk markers) → 1 (many risk markers). Not a calibrated probability. */
    score: number | null;
    /** Only present when the producing model reports one. Never synthesised. */
    confidence: number | null;
    needsVerification: boolean;
    reasoning: string | null;
}

export interface Article {
    id: string;
    title: string;
    publisher: string;
    sourceUrl: string | null;
    imageUrl: string | null;
    /** Text supplied by the publisher's feed (RSS description). Never a full article body. */
    excerpt: string;
    /** Machine summary, when one exists. `summaryKind` says how it was produced. */
    summary: string | null;
    summaryKind: 'ai' | 'extractive' | null;
    section: SectionSlug;
    author: string | null;
    publishedAt: string | null;
    ingestedAt: string | null;
    sentiment: Sentiment | null;
    credibility: CredibilityAssessment;
    dimensions: DimensionScores | null;
    groupId: string | null;
    eventTitle: string | null;
    origin: ArticleOrigin;
    analysisMethod: AnalysisMethod;
}

export interface ArticleGroup {
    groupId: string;
    eventTitle: string;
    articles: Article[];
    publishers: string[];
}

export interface ArticleQuery {
    q?: string;
    section?: SectionSlug | '';
    publisher?: string;
    risk?: RiskLabel | '';
    needsVerification?: boolean;
    /** Searches default to relevance; listings without a query default to newest. */
    sort?: 'relevance' | 'newest' | 'oldest';
    since?: '24h' | '7d' | '30d';
    page?: number;
    limit?: number;
}

export interface ArticlePage {
    articles: Article[];
    total: number;
    /** Leading entries that match every search term; later entries are partial matches. */
    fullMatches: number;
    page: number;
    limit: number;
    hasMore: boolean;
}

export interface EditionInfo {
    origin: ArticleOrigin;
    fetchedAt: string;
    articleCount: number;
    publisherCount: number;
    /** Feeds that could not be reached in the last refresh. */
    failedSources: string[];
}

export interface AnalyticsSummary {
    edition: EditionInfo;
    sections: { section: SectionSlug; count: number }[];
    risk: { label: RiskLabel | 'Needs Verification'; count: number }[];
    sentiment: { sentiment: Sentiment | 'unscored'; count: number }[];
    dimensionAverages: { key: DimensionKey; average: number; n: number }[];
    publishers: { publisher: string; count: number }[];
    timeline: { hour: string; count: number }[];
    coverage: {
        groups: number;
        articlesInGroups: number;
        largestGroup: number;
        publishersPerGroup: { publishers: number; groups: number }[];
    };
    analysisMethods: { method: AnalysisMethod; count: number }[];
}
