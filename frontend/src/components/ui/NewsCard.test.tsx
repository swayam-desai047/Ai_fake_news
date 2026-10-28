import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, it, expect, vi } from 'vitest'
import NewsCard from './NewsCard'
import type { Article } from '@/lib/types'

vi.mock('next/link', () => ({
    default: ({ href, children, ...rest }: { href: string; children: React.ReactNode }) => <a href={href} {...rest}>{children}</a>,
}))

const base: Article = {
    id: 'lv-test',
    title: 'Test Headline AI',
    publisher: 'example.com',
    sourceUrl: 'https://example.com/story',
    imageUrl: null,
    excerpt: 'This is a test summary for the AI project.',
    summary: null,
    summaryKind: null,
    section: 'technology',
    author: null,
    publishedAt: '2023-10-01T10:00:00Z',
    ingestedAt: null,
    sentiment: 'positive',
    credibility: { label: 'Low Risk', score: 0.1, confidence: null, needsVerification: false, reasoning: null },
    dimensions: null,
    groupId: null,
    eventTitle: null,
    origin: 'live-feed',
    analysisMethod: 'heuristic',
}

afterEach(cleanup)

describe('NewsCard', () => {
    it('renders the headline, excerpt and publisher', () => {
        render(<NewsCard article={base} />)

        expect(screen.getByText('Test Headline AI')).toBeInTheDocument()
        expect(screen.getByText('This is a test summary for the AI project.')).toBeInTheDocument()
        expect(screen.getByText('example.com')).toBeInTheDocument()
    })

    it('shows the risk label and states that confidence was not reported', () => {
        render(<NewsCard article={base} />)

        expect(screen.getByText('Low Risk')).toBeInTheDocument()
        expect(screen.getByText(/Confidence not reported/)).toBeInTheDocument()
        expect(screen.queryByText('Needs verification')).not.toBeInTheDocument()
    })

    it('shows high risk and the verification flag separately', () => {
        render(<NewsCard article={{ ...base, credibility: { label: 'High Risk', score: 0.8, confidence: 0.55, needsVerification: true, reasoning: null } }} />)

        expect(screen.getByText('High Risk')).toBeInTheDocument()
        expect(screen.getByText('Needs verification')).toBeInTheDocument()
        expect(screen.getByText(/Confidence 55%/)).toBeInTheDocument()
    })
})
