import type { SectionSlug } from './types';

export interface FeedSource {
    publisher: string;
    url: string;
}

export interface SectionDef {
    slug: SectionSlug;
    label: string;
    /** Heading used on the front page and section fronts. */
    heading: string;
    feeds: FeedSource[];
}

/**
 * The publication's section index. Each section is backed by real publisher RSS feeds;
 * nothing is shown for a section unless those feeds return stories.
 */
export const SECTIONS: SectionDef[] = [
    {
        slug: 'world',
        label: 'World',
        heading: 'World News',
        feeds: [
            { publisher: 'Google News (World)', url: 'https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/world/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/world/rss' },
            { publisher: 'Al Jazeera', url: 'https://www.aljazeera.com/xml/rss/all.xml' },
            { publisher: 'The Hindu', url: 'https://www.thehindu.com/news/international/feeder/default.rss' },
        ],
    },
    {
        slug: 'india',
        label: 'India',
        heading: 'India News',
        feeds: [
            { publisher: 'Google News (India)', url: 'https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en' },
            { publisher: 'The Hindu', url: 'https://www.thehindu.com/news/national/feeder/default.rss' },
            { publisher: 'NDTV', url: 'https://feeds.feedburner.com/ndtvnews-india-news' },
            { publisher: 'The Indian Express', url: 'https://indianexpress.com/section/india/feed/' },
        ],
    },
    {
        slug: 'politics',
        label: 'Politics',
        heading: 'Politics',
        feeds: [
            { publisher: 'Google News (Politics)', url: 'https://news.google.com/rss/search?q=politics&hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/politics/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/politics/rss' },
        ],
    },
    {
        slug: 'business',
        label: 'Business',
        heading: 'Business & Markets',
        feeds: [
            { publisher: 'Google News (Business)', url: 'https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/business/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/business/rss' },
            { publisher: 'Mint', url: 'https://www.livemint.com/rss/markets' },
            { publisher: 'The Hindu', url: 'https://www.thehindu.com/business/feeder/default.rss' },
        ],
    },
    {
        slug: 'technology',
        label: 'Technology',
        heading: 'Technology',
        feeds: [
            { publisher: 'Google News (Technology)', url: 'https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/technology/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/technology/rss' },
            { publisher: 'TechCrunch', url: 'https://techcrunch.com/feed/' },
            { publisher: 'The Hindu', url: 'https://www.thehindu.com/sci-tech/technology/feeder/default.rss' },
        ],
    },
    {
        slug: 'science',
        label: 'Science',
        heading: 'Science & Environment',
        feeds: [
            { publisher: 'Google News (Science)', url: 'https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/science/rss' },
        ],
    },
    {
        slug: 'culture',
        label: 'Culture',
        heading: 'Culture',
        feeds: [
            { publisher: 'Google News (Culture)', url: 'https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC News', url: 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/culture/rss' },
        ],
    },
    {
        slug: 'sports',
        label: 'Sports',
        heading: 'Sports',
        feeds: [
            { publisher: 'Google News (Sports)', url: 'https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US&ceid=US:en' },
            { publisher: 'BBC Sport', url: 'https://feeds.bbci.co.uk/sport/rss.xml' },
            { publisher: 'The Guardian', url: 'https://www.theguardian.com/sport/rss' },
        ],
    },
];

export const SECTION_SLUGS = SECTIONS.map(s => s.slug);

export function getSection(slug: string | undefined | null): SectionDef | undefined {
    if (!slug) return undefined;
    return SECTIONS.find(s => s.slug === slug.toLowerCase());
}

export function sectionLabel(slug: SectionSlug): string {
    return getSection(slug)?.label ?? slug;
}

/**
 * Maps the backend's ingestion categories (see backend/services/rss_fetcher.py) onto the
 * publication's sections. The backend files general world news under `general`.
 */
export function sectionFromCategory(category: string | null | undefined): SectionSlug {
    const c = (category || '').toLowerCase().trim();
    if (c === 'general' || c === 'world' || c === '') return 'world';
    if (c === 'tech') return 'technology';
    if (c === 'sport') return 'sports';
    if (c === 'entertainment' || c === 'arts') return 'culture';
    return getSection(c)?.slug ?? 'world';
}
