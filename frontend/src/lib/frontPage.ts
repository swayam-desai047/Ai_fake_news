import type { Edition } from './repository';
import { SECTIONS, type SectionDef } from './sections';
import type { Article, ArticleGroup } from './types';

/**
 * Composes the front page from the edition. Every article appears at most once on the page;
 * sections are only printed when enough unused stories remain to fill them.
 */

export type SectionLayout = 'a' | 'b' | 'c' | 'd';

export interface FrontSection {
    section: SectionDef;
    layout: SectionLayout;
    articles: Article[];
}

export interface FrontPage {
    lead: Article | null;
    leadGroup: ArticleGroup | null;
    supporting: Article[];
    latest: Article[];
    daily: Article[];
    featured: Article[];
    mostCovered: ArticleGroup[];
    sections: FrontSection[];
}

const HARD_NEWS = new Set(['world', 'india', 'politics', 'business']);
const LAYOUT_ROTATION: SectionLayout[] = ['a', 'c', 'b', 'd'];
const LAYOUT_SIZE: Record<SectionLayout, number> = { a: 5, b: 7, c: 7, d: 8 };
const MIN_SECTION_STORIES = 4;

export function composeFrontPage(edition: Edition, now = Date.now()): FrontPage {
    const used = new Set<string>();
    const available = () => edition.articles.filter(a => !used.has(a.id));
    const mark = <T extends Article>(a: T): T => {
        used.add(a.id);
        return a;
    };

    // Lead: the most recent widely covered event with a photograph; otherwise the newest photo story.
    let lead: Article | null = null;
    let leadGroup: ArticleGroup | null = null;
    const recent = (a: Article) => !a.publishedAt || now - Date.parse(a.publishedAt) < 12 * 3600_000;

    const groupTime = (g: ArticleGroup) => Math.max(0, ...g.articles.map(a => Date.parse(a.publishedAt ?? '') || 0));
    const sortedGroups = [...edition.groups].sort((a, b) => {
        const tA = groupTime(a);
        const tB = groupTime(b);
        const recentA = tA > 0 && now - tA < 8 * 3600_000;
        const recentB = tB > 0 && now - tB < 8 * 3600_000;
        if (recentA && !recentB) return -1;
        if (!recentA && recentB) return 1;
        if (tA && tB && Math.abs(tB - tA) > 2 * 3600_000) return tB - tA;
        return b.publishers.length - a.publishers.length;
    });

    for (const g of sortedGroups) {
        const pick = g.articles.find(a => a.imageUrl && recent(a));
        if (pick) {
            lead = pick;
            leadGroup = g;
            break;
        }
    }
    if (!lead) lead = available().find(a => a.imageUrl && HARD_NEWS.has(a.section)) ?? available()[0] ?? null;
    if (lead) mark(lead);
    // Other reports of the lead event are represented by the lead, not repeated elsewhere.
    leadGroup?.articles.forEach(a => used.add(a.id));

    const supporting = available()
        .filter(a => a.imageUrl && HARD_NEWS.has(a.section))
        .slice(0, 3)
        .map(mark);

    const daily: Article[] = [];
    for (const s of SECTIONS) {
        if (daily.length >= 7) break;
        const pick = available().find(a => a.section === s.slug && !daily.some(d => d.section === s.slug));
        if (pick) daily.push(mark(pick));
    }

    const latest = available().slice(0, 12).map(mark);

    // Featured: photo stories, rotating through sections for range.
    const featured: Article[] = [];
    const bySection = new Map(SECTIONS.map(s => [s.slug, available().filter(a => a.imageUrl && a.section === s.slug)]));
    while (featured.length < 8) {
        let added = false;
        for (const s of SECTIONS) {
            const next = bySection.get(s.slug)?.find(a => !used.has(a.id));
            if (next && featured.length < 8) {
                featured.push(mark(next));
                added = true;
            }
        }
        if (!added) break;
    }
    // A four-column grid reads best with complete rows.
    while (featured.length % 4 !== 0 && featured.length > 4) used.delete(featured.pop()!.id);

    const mostCovered = edition.groups.filter(g => g.groupId !== leadGroup?.groupId).slice(0, 3);

    const sections: FrontSection[] = [];
    let rotation = 0;
    for (const section of SECTIONS) {
        const pool = available().filter(a => a.section === section.slug);
        if (pool.length < MIN_SECTION_STORIES) continue;
        const layout = LAYOUT_ROTATION[rotation++ % LAYOUT_ROTATION.length];
        // Image-led layouts want a photograph in the lead slot.
        const ordered = [...pool.filter(a => a.imageUrl), ...pool.filter(a => !a.imageUrl)];
        const picked = (layout === 'b' ? pool : ordered).slice(0, LAYOUT_SIZE[layout]).map(mark);
        sections.push({ section, layout, articles: picked });
    }

    return { lead, leadGroup, supporting, latest, daily, featured, mostCovered, sections };
}
