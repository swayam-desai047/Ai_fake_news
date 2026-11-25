import { describe, expect, it } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { analyseText } from './scoring';

/**
 * The backend (backend/services/dimension_service.py) mirrors scoring.ts. Both test suites check
 * their output against shared/scoring_vectors.json so the two implementations cannot drift apart.
 * Regenerate after an intentional change with: WRITE_VECTORS=1 npx vitest run src/lib/scoringParity.test.ts
 */
const FILE = resolve(__dirname, '../../../shared/scoring_vectors.json');

const INPUTS: [string, string, string][] = [
    ['Parliament passes budget', 'Lawmakers approved the budget on Tuesday, officials said, after a long debate over spending plans and taxes for the coming year.', 'BBC News'],
    ['SHOCKING!!! You won’t believe this secret', 'Exposed.', 'Unknown Blog'],
    ['Headline only story about markets', '', 'Reuters'],
    ['Headline only story about markets', '', 'Some Blog'],
    ['Markets rally as inflation cools', 'Stocks rose sharply on Wednesday after new data showed inflation easing for a third month. Analysts said the figures boost hopes of a rate cut. The index gained 2% in early trading, according to exchange data.', 'Bloomberg'],
    ['Regime thugs crush protest in brutal crackdown', 'The so-called government sent its mob to attack peaceful protesters. It was a horrific and disgraceful display of terror. Obviously the elites do not care.', 'Patriot Daily'],
    ['Scientists report breakthrough in battery research', 'Researchers at the university announced a new battery chemistry that could improve storage. The team said the results were confirmed in independent tests.', 'The Hindu'],
    ['URGENT: Celebrity DESTROYS critics in viral clip', 'The clip goes viral as fans celebrate. Must see!!', 'TMZ Gossip'],
    ['Flood warning issued as river rises', 'Officials warned residents near the river to prepare for possible evacuation after heavy rain. The water level rose by two metres overnight, the agency said.', 'NDTV'],
    ['Same title', 'Same title', 'CNN'],
];

describe('scoring parity vectors', () => {
    it('matches shared/scoring_vectors.json', () => {
        const actual = INPUTS.map(([title, excerpt, publisher]) => ({ title, excerpt, publisher, expected: analyseText(title, excerpt, publisher) }));
        if (process.env.WRITE_VECTORS) writeFileSync(FILE, JSON.stringify(actual, null, 2) + '\n');
        const stored = JSON.parse(readFileSync(FILE, 'utf8'));
        expect(actual).toEqual(stored);
    });
});
