/** Date and number formatting. The edition is dated in Indian Standard Time. */

export const EDITION_TZ = 'Asia/Kolkata';
export const EDITION_TZ_LABEL = 'IST';

export function editionDate(d: Date | string = new Date()): string {
    return new Intl.DateTimeFormat('en-GB', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: EDITION_TZ,
    }).format(new Date(d));
}

export function clockTime(d: Date | string | null | undefined): string {
    if (!d) return '';
    const date = new Date(d);
    if (Number.isNaN(date.getTime())) return '';
    return new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: EDITION_TZ }).format(date);
}

export function dateTime(d: string | null | undefined): string {
    if (!d) return 'Date not supplied';
    const date = new Date(d);
    if (Number.isNaN(date.getTime())) return 'Date not supplied';
    return `${new Intl.DateTimeFormat('en-GB', {
        day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: EDITION_TZ,
    }).format(date)} ${EDITION_TZ_LABEL}`;
}

export function timeAgo(d: string | null | undefined, now = Date.now()): string {
    if (!d) return '';
    const t = Date.parse(d);
    if (!Number.isFinite(t)) return '';
    const mins = Math.round((now - t) / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins} min ago`;
    const hrs = Math.round(mins / 60);
    if (hrs < 24) return `${hrs} hr${hrs === 1 ? '' : 's'} ago`;
    const days = Math.round(hrs / 24);
    if (days < 7) return `${days} day${days === 1 ? '' : 's'} ago`;
    return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', timeZone: EDITION_TZ }).format(new Date(t));
}

/** Volume / issue numbering derived from the publication's launch date. */
const LAUNCH = Date.UTC(2026, 0, 1);
export function editionNumber(d: Date = new Date()): { volume: string; issue: number } {
    const days = Math.max(1, Math.floor((d.getTime() - LAUNCH) / 86400000) + 1);
    return { volume: 'I', issue: days };
}

export function pct(n: number | null | undefined): string {
    return typeof n === 'number' ? `${Math.round(n * 100)}%` : '—';
}

export function truncateWords(text: string, maxChars: number): string {
    if (text.length <= maxChars) return text;
    const cut = text.slice(0, maxChars);
    return `${cut.slice(0, cut.lastIndexOf(' ')).replace(/[,.;:–—-]$/, '')}…`;
}
