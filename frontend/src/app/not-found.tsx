import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="np-container py-16">
            <div className="notice max-w-2xl mx-auto">
                <p className="kicker">Not in this edition</p>
                <h1 className="hl-1 mt-3">We could not find that page</h1>
                <p className="dek mt-4">
                    Live stories leave the edition as publishers update their feeds. The story may have rotated out,
                    or the address may be mistyped.
                </p>
                <div className="mt-6 flex justify-center gap-4">
                    <Link href="/" className="btn">Front page</Link>
                    <Link href="/search" className="btn btn--ghost">Search</Link>
                </div>
            </div>
        </div>
    );
}
