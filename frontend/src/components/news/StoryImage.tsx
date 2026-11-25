'use client';

import { useEffect, useRef, useState } from 'react';
import type { Article } from '@/lib/types';
import { sectionLabel } from '@/lib/sections';

interface StoryImageProps {
    article: Pick<Article, 'imageUrl' | 'publisher' | 'section'>;
    ratio?: 'standard' | 'wide' | 'square';
    priority?: boolean;
    className?: string;
    style?: React.CSSProperties;
    credit?: boolean;
}

/**
 * The publisher's own photograph, or — when the feed supplied none, or it fails to load —
 * a typographic plate. Never a substitute stock image.
 */
export default function StoryImage({ article, ratio = 'standard', priority = false, className = '', style, credit = false }: StoryImageProps) {
    // 0 = direct, 1 = via public image proxy (publisher host blocked on some networks), 2 = give up.
    const [attempt, setAttempt] = useState(0);
    const imgRef = useRef<HTMLImageElement>(null);
    // A server-rendered <img> can fail before hydration attaches onError; catch that case on mount.
    useEffect(() => {
        const img = imgRef.current;
        // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing with a DOM load error that happened pre-hydration
        if (img?.complete && img.naturalWidth === 0) setAttempt(a => (a === 0 ? 1 : a));
    }, []);
    const showImage = Boolean(article.imageUrl) && attempt < 2;
    const src = attempt === 0 ? article.imageUrl! : `https://wsrv.nl/?url=${encodeURIComponent(article.imageUrl ?? '')}`;
    const frame = ratio === 'wide' ? 'img-frame img-frame--wide' : ratio === 'square' ? 'img-frame img-frame--square' : 'img-frame';

    return (
        <figure className={`figure ${className}`} style={style}>
            <div className={frame}>
                {showImage ? (
                    // Publisher images come from many hosts; a plain <img> avoids an image-proxy allowlist.
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        ref={imgRef}
                        src={src}
                        alt=""
                        loading={priority ? 'eager' : 'lazy'}
                        fetchPriority={priority ? 'high' : 'auto'}
                        decoding="async"
                        referrerPolicy="no-referrer"
                        onError={() => setAttempt(a => a + 1)}
                    />
                ) : (
                    <div className="plate" aria-hidden>
                        <span className="plate__section">{sectionLabel(article.section)}</span>
                        <span className="plate__publisher">{article.publisher}</span>
                    </div>
                )}
            </div>
            {credit && showImage && <figcaption className="figcaption">Photograph: {article.publisher}</figcaption>}
        </figure>
    );
}
