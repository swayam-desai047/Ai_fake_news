'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { Search } from 'lucide-react';
import { SECTIONS } from '@/lib/sections';

const ITEMS = [
    { href: '/', label: 'Home' },
    ...SECTIONS.map(s => ({ href: `/section/${s.slug}`, label: s.label })),
    { href: '/compare', label: 'Coverage' },
    { href: '/analytics', label: 'Analysis' },
];

function isActive(pathname: string, href: string): boolean {
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(`${href}/`);
}

/** Sticky section index. Shows a small nameplate once the masthead has scrolled away. */
export default function SectionNav() {
    const pathname = usePathname() || '/';
    const [condensed, setCondensed] = useState(false);
    const listRef = useRef<HTMLUListElement>(null);

    useEffect(() => {
        const masthead = document.querySelector('[data-masthead]');
        if (!masthead) return;
        const io = new IntersectionObserver(([entry]) => setCondensed(!entry.isIntersecting), { threshold: 0 });
        io.observe(masthead);
        return () => io.disconnect();
    }, []);

    // Keep the active section visible in the horizontally scrolling index on small screens.
    useEffect(() => {
        const active = listRef.current?.querySelector<HTMLElement>('[aria-current="page"]');
        active?.scrollIntoView({ block: 'nearest', inline: 'center' });
    }, [pathname]);

    return (
        <nav className="secnav no-print enter-fade" style={{ '--d': '360ms' } as React.CSSProperties} aria-label="Sections" data-condensed={condensed}>
            <div className="np-container secnav__inner">
                <Link href="/" className="secnav__mini" tabIndex={condensed ? 0 : -1} aria-hidden={!condensed}>
                    The Daily Signal
                </Link>
                <ul className="secnav__list" ref={listRef}>
                    {ITEMS.map(item => (
                        <li key={item.href} className="secnav__item">
                            <Link
                                href={item.href}
                                className="secnav__link"
                                aria-current={isActive(pathname, item.href) ? 'page' : undefined}
                            >
                                {item.label}
                            </Link>
                        </li>
                    ))}
                </ul>
                <Link href="/search" className="secnav__search" aria-current={pathname === '/search' ? 'page' : undefined}>
                    <Search size={14} strokeWidth={2} aria-hidden />
                    <span className="hidden lg:inline">Search</span>
                    <span className="sr-only lg:hidden">Search</span>
                </Link>
            </div>
        </nav>
    );
}
