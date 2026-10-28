/** Shown while a search is running on the server. */
export default function SearchLoading() {
    return (
        <div className="np-container pt-8" role="status" aria-busy="true">
            <p className="kicker">Search</p>
            <p className="hl-lead mt-2">Searching the edition…</p>
            <div className="mt-8 space-y-4">
                {[0, 1, 2, 3].map(i => <div key={i} className="skeleton h-20" />)}
            </div>
        </div>
    );
}
