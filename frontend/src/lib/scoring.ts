import type { CredibilityAssessment, DimensionScores, RiskLabel, Sentiment } from './types';

/**
 * Transparent lexical analysis used for live-feed articles that have not passed through the
 * backend's model pipeline. Every number here is reproducible from the article text and the
 * publisher name; nothing is randomised and no confidence value is invented.
 *
 * Score direction (0–100) per dimension:
 *  - sentiment:          0 = strongly negative tone, 50 = neutral, 100 = strongly positive
 *  - bias:               100 = no loaded or one-sided language detected
 *  - objectivity:        100 = no evaluative / subjective wording detected
 *  - readability:        Flesch Reading Ease (higher = easier to read, not "better")
 *  - propaganda:         100 = no manipulation or sensationalism markers detected
 *  - headline_accuracy:  share of headline terms supported by the excerpt
 *  - source_credibility: publisher reputation from a hand-curated reference table
 *  - content_quality:    completeness of the supplied excerpt (not the full article)
 */

/** Hand-curated reference table (handover §6 step 2: "domain authority dictionary"). */
const PUBLISHER_REPUTATION: [string, number][] = [
    ['reuters', 95],
    ['associated press', 95],
    ['bbc', 93],
    ['guardian', 90],
    ['the hindu', 90],
    ['financial times', 93],
    ['bloomberg', 92],
    ['indian express', 88],
    ['al jazeera', 86],
    ['ndtv', 84],
    ['mint', 86],
    ['techcrunch', 84],
    ['cnn', 86],
    ['yahoo', 78],
];
const UNKNOWN_PUBLISHER_SCORE = 60;

const POSITIVE = ['surge', 'gain', 'gains', 'milestone', 'breakthrough', 'success', 'record', 'win', 'wins', 'won', 'growth', 'rise', 'rises', 'improve', 'improves', 'celebrate', 'recovery', 'hope', 'boost', 'praise', 'award', 'agreement', 'deal'];
const NEGATIVE = ['crash', 'collapse', 'death', 'dead', 'dies', 'died', 'killed', 'kill', 'fraud', 'theft', 'warning', 'ban', 'threat', 'scandal', 'loss', 'arrest', 'arrested', 'panic', 'terror', 'attack', 'war', 'crisis', 'fall', 'falls', 'cut', 'cuts', 'fear', 'fears', 'violence', 'shooting', 'injured', 'sanction', 'sanctions', 'protest', 'accused', 'condemns'];
const SUBJECTIVE = ['obviously', 'clearly', 'terrible', 'wonderful', 'disastrous', 'miracle', 'heroic', 'shameful', 'absurd', 'brilliant', 'outrageous', 'pathetic', 'incredible', 'unbelievable', 'amazing', 'horrific', 'disgraceful'];
const LOADED = ['regime', 'radical', 'extremist', 'thugs', 'elites', 'puppet', 'traitor', 'propaganda', 'so-called', 'mob', 'witch hunt', 'invasion'];
const ATTRIBUTION = ['said', 'says', 'according to', 'told', 'stated', 'reported', 'announced', 'confirmed', 'spokesperson', 'officials'];
const MANIPULATION: RegExp[] = [
    /\bshocking\b/i, /\byou won'?t believe\b/i, /\bsecret\b/i, /\burgent\b/i, /\bexposed\b/i,
    /\boutrage\b/i, /!{2,}/, /\bmust see\b/i, /\bgoes viral\b/i, /\bdestroys\b/i, /\bslams\b/i,
];

const STOPWORDS = new Set('a an the and or but of to in on at for with by from as is are was were be been it its this that these those after before over under into about than then will would could should may might has have had not no yes up out new says say said what how why who when where which'.split(' '));

function words(text: string): string[] {
    return text.toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').split(/\s+/).filter(Boolean);
}

function countHits(text: string, list: string[]): number {
    let n = 0;
    for (const term of list) {
        const re = term.includes(' ') ? new RegExp(term, 'i') : new RegExp(`\\b${term}\\b`, 'i');
        if (re.test(text)) n++;
    }
    return n;
}

const clamp = (n: number, lo = 0, hi = 100) => Math.max(lo, Math.min(hi, Math.round(n)));

function syllables(word: string): number {
    const w = word.toLowerCase().replace(/[^a-z]/g, '');
    if (!w) return 0;
    const m = w.replace(/(?:[^laeiouy]|ed|es|e)$/, '').replace(/^y/, '').match(/[aeiouy]{1,2}/g);
    return Math.max(1, m?.length ?? 1);
}

function fleschReadingEase(text: string): number {
    const ws = text.trim().split(/\s+/).filter(Boolean);
    if (ws.length === 0) return 50;
    const sentences = Math.max(1, text.split(/[.!?]+/).filter(s => s.trim()).length);
    const syl = ws.reduce((acc, w) => acc + syllables(w), 0);
    return 206.835 - 1.015 * (ws.length / sentences) - 84.6 * (syl / ws.length);
}

export function publisherReputation(publisher: string): number | null {
    const p = publisher.toLowerCase();
    for (const [key, score] of PUBLISHER_REPUTATION) {
        if (p.includes(key)) return score;
    }
    return null;
}

export function splitSentences(text: string): string[] {
    return text
        .split(/(?<=[.!?])\s+(?=[A-Z0-9“"'‘])/)
        .map(s => s.trim())
        .filter(s => s.length > 0);
}

/** Extractive summary: only produced when the excerpt is long enough to be condensed. */
export function extractiveSummary(excerpt: string): string | null {
    const sentences = splitSentences(excerpt).filter(s => s.length > 30);
    if (sentences.length < 3) return null;
    return sentences.slice(0, 2).join(' ');
}

/** Handover §6 thresholds for mapping a risk score onto a label. */
export function riskLabelFor(score: number): RiskLabel {
    if (score <= 0.35) return 'Low Risk';
    if (score <= 0.65) return 'Moderate Risk';
    return 'High Risk';
}

/** Below this many characters of supplied text the heuristic has too little evidence to rely on. */
export const MIN_EVIDENCE_CHARS = 150;

export interface HeuristicResult {
    sentiment: Sentiment;
    dimensions: DimensionScores;
    credibility: CredibilityAssessment;
}

export function analyseText(title: string, excerpt: string, publisher: string): HeuristicResult {
    const body = excerpt && excerpt !== title ? excerpt : '';
    const combined = `${title}. ${body}`;
    const evidenceChars = body.length;

    // 1. Sentiment (direction, not quality)
    const pos = countHits(combined, POSITIVE);
    const neg = countHits(combined, NEGATIVE);
    const sentimentScore = clamp(50 + (pos - neg) * 9, 5, 95);
    const sentiment: Sentiment = sentimentScore >= 60 ? 'positive' : sentimentScore <= 40 ? 'negative' : 'neutral';
    const sentimentExpl = sentiment === 'neutral'
        ? `Balanced or descriptive tone (${pos} positive, ${neg} negative cue words).`
        : `Predominantly ${sentiment} framing: ${pos} positive and ${neg} negative cue words.`;

    // 2. Objectivity
    const subj = countHits(combined, SUBJECTIVE);
    const objectivity = clamp(92 - subj * 14, 20);
    const objectivityExpl = subj > 0
        ? `${subj} evaluative adjective${subj > 1 ? 's' : ''} found; wording leans on judgement rather than fact.`
        : 'No evaluative adjectives from the reference lexicon were found.';

    // 3. Bias (loaded vocabulary + whether claims are attributed)
    const loaded = countHits(combined, LOADED);
    const attributed = countHits(combined, ATTRIBUTION) > 0;
    const bias = clamp(90 - loaded * 15 - (attributed || !body ? 0 : 6), 20);
    const biasExpl = loaded > 0
        ? `${loaded} loaded or partisan term${loaded > 1 ? 's' : ''} detected.`
        : attributed
            ? 'No loaded terms; claims carry explicit attribution.'
            : 'No loaded terms detected; the excerpt does not attribute its claims.';

    // 4. Readability
    const flesch = fleschReadingEase(combined);
    const readability = clamp(flesch);
    const readabilityExpl = `Flesch Reading Ease ${Math.round(flesch)} — ${readability >= 60 ? 'plain, accessible prose' : readability >= 40 ? 'moderately demanding prose' : 'dense, technical prose'}.`;

    // 5. Propaganda / manipulation
    const manip = MANIPULATION.filter(re => re.test(combined)).length;
    const shouting = (title.match(/\b[A-Z]{5,}\b/g) || []).length;
    const propaganda = clamp(95 - manip * 22 - shouting * 10, 5);
    const propagandaExpl = manip + shouting > 0
        ? `${manip + shouting} sensationalism marker${manip + shouting > 1 ? 's' : ''} (clickbait phrasing, shouting capitals or stacked exclamation).`
        : 'No clickbait phrasing, shouting capitals or stacked exclamation detected.';

    // 6. Headline accuracy
    const headTerms = words(title).filter(w => w.length > 3 && !STOPWORDS.has(w));
    const bodyTerms = new Set(words(body));
    const matched = headTerms.filter(t => bodyTerms.has(t) || bodyTerms.has(t.replace(/s$/, ''))).length;
    const ratio = headTerms.length ? matched / headTerms.length : 0;
    const headline_accuracy = body ? clamp(45 + ratio * 50) : 50;
    const headlineExpl = body
        ? `${matched} of ${headTerms.length} key headline terms appear in the excerpt.`
        : 'No excerpt supplied, so the headline could not be checked against body text.';

    // 7. Source credibility
    const rep = publisherReputation(publisher);
    const source_credibility = rep ?? UNKNOWN_PUBLISHER_SCORE;
    const sourceExpl = rep !== null
        ? `${publisher} is listed in the publication's reference table of established newsrooms.`
        : `${publisher || 'This publisher'} is not in the reference table; treated as unrated.`;

    // 8. Content quality (of the excerpt we were given)
    const sentences = splitSentences(body).length;
    const content_quality = clamp(35 + Math.min(evidenceChars, 600) / 12 + Math.min(sentences, 4) * 5);
    const contentExpl = evidenceChars < MIN_EVIDENCE_CHARS
        ? `Feed supplied only ${evidenceChars} characters; quality of the full article cannot be judged.`
        : `Feed excerpt of ${evidenceChars} characters across ${sentences} sentence${sentences === 1 ? '' : 's'}.`;

    const dimensions: DimensionScores = {
        sentiment: sentimentScore,
        bias,
        objectivity,
        readability,
        propaganda,
        headline_accuracy,
        source_credibility,
        content_quality,
        explanations: {
            sentiment: sentimentExpl,
            bias: biasExpl,
            objectivity: objectivityExpl,
            readability: readabilityExpl,
            propaganda: propagandaExpl,
            headline_accuracy: headlineExpl,
            source_credibility: sourceExpl,
            content_quality: contentExpl,
        },
    };

    // Risk: inverse of a weighted composite of the dimensions that bear on credibility.
    const composite = (
        source_credibility * 0.35 +
        propaganda * 0.2 +
        objectivity * 0.15 +
        bias * 0.15 +
        headline_accuracy * 0.15
    ) / 100;
    const score = Math.round((1 - composite) * 100) / 100;
    const label = riskLabelFor(score);
    const ambiguous = score >= 0.4 && score <= 0.6;
    const thin = evidenceChars < MIN_EVIDENCE_CHARS;
    const needsVerification = ambiguous || thin;

    const reasons: string[] = [];
    reasons.push(`Rule-based risk score ${score.toFixed(2)} (${label}).`);
    if (thin) reasons.push(`Only ${evidenceChars} characters of publisher text were available, below the ${MIN_EVIDENCE_CHARS}-character evidence threshold.`);
    if (ambiguous) reasons.push('The score falls inside the 0.40–0.60 uncertainty band.');
    if (manip + shouting > 0) reasons.push('Sensational framing markers were found.');
    if (rep === null) reasons.push('The publisher is not in the reference reputation table.');

    return {
        sentiment,
        dimensions,
        credibility: {
            label,
            score,
            confidence: null,
            needsVerification,
            reasoning: reasons.join(' '),
        },
    };
}
