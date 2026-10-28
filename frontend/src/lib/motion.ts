import type { CSSProperties } from 'react';

/** Inline custom property for staggered entrance animations (`.enter`, `.enter-img`, …). */
export function delay(ms: number): CSSProperties {
    return { '--d': `${ms}ms` } as CSSProperties;
}
