'use client';

import { useState } from 'react';
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
    const [failed, setFailed] = useState(false);
    const showImage = Boolean(article.imageUrl) && !failed;
    const frame = ratio === 'wide' ? 'img-frame img-frame--wide' : ratio === 'square' ? 'img-frame img-frame--square' : 'img-frame';

    return (
        <figure className={`figure ${className}`} style={style}>
            <div className={frame}>
                {showImage ? (
                    // Publisher images come from many hosts; a plain <img> avoids an image-proxy allowlist.
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        src={article.imageUrl!}
                        alt=""
                        loading={priority ? 'eager' : 'lazy'}
                        fetchPriority={priority ? 'high' : 'auto'}
                        decoding="async"
                        referrerPolicy="no-referrer"
                        onError={() => setFailed(true)}
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
