/** Newspaper-shaped placeholder while the edition is assembled. */
export default function Loading() {
    return (
        <div className="np-container pt-6" aria-busy="true" aria-label="Loading the edition">
            <div className="front">
                <div className="front__latest space-y-4">
                    {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton h-12" />)}
                </div>
                <div className="front__lead">
                    <div className="skeleton aspect-video" />
                    <div className="skeleton h-10 mt-4 w-4/5" />
                    <div className="skeleton h-4 mt-3" />
                    <div className="skeleton h-4 mt-2 w-2/3" />
                </div>
                <div className="front__feed space-y-5">
                    {Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton h-16" />)}
                </div>
            </div>
        </div>
    );
}
