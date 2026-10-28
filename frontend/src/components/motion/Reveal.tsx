'use client';

import { useEffect, useRef, type CSSProperties, type ElementType, type HTMLAttributes, type ReactNode } from 'react';

interface RevealProps extends HTMLAttributes<HTMLElement> {
    children: ReactNode;
    as?: ElementType;
    delay?: number;
}

/** One-shot scroll reveal (IntersectionObserver). Content is fully visible without JS. */
export default function Reveal({ children, as: Tag = 'div', delay = 0, style, ...rest }: RevealProps) {
    const ref = useRef<HTMLElement>(null);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;
        if (!('IntersectionObserver' in window)) {
            el.classList.add('is-visible');
            return;
        }
        const io = new IntersectionObserver(
            entries => {
                for (const entry of entries) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        io.unobserve(entry.target);
                    }
                }
            },
            { rootMargin: '0px 0px -8% 0px', threshold: 0.06 },
        );
        io.observe(el);
        return () => io.disconnect();
    }, []);

    return (
        <Tag ref={ref} data-reveal {...rest} style={{ ...style, '--d': `${delay}ms` } as CSSProperties}>
            {children}
        </Tag>
    );
}
