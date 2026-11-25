import { DIMENSIONS } from '@/lib/dimensions';
import type { DimensionScores } from '@/lib/types';

/** Exact scores, scale meaning and the explanation for each of the eight dimensions. */
export default function DimensionTable({ dimensions }: { dimensions: DimensionScores }) {
    return (
        <table className="score-table">
            <caption className="sr-only">Eight-dimension content analysis scores with explanations</caption>
            <thead>
                <tr>
                    <th scope="col" className="w-[36%]">Dimension</th>
                    <th scope="col" className="w-[12%] text-right pr-4">Score</th>
                    <th scope="col">Reading</th>
                </tr>
            </thead>
            <tbody>
                {DIMENSIONS.map(d => {
                    const score = dimensions[d.key];
                    return (
                        <tr key={d.key}>
                            <th scope="row" className="!font-serif !text-[0.98rem] !normal-case !tracking-normal !text-[var(--ink)] !font-semibold !border-b-[var(--rule)] pr-3">
                                {d.label}
                                <div className="score-bar mt-2" aria-hidden>
                                    {score !== null && <div className="score-bar__fill" style={{ width: `${score}%` }} />}
                                    {d.bipolar && <div className="score-bar__mid" />}
                                </div>
                                <div className="flex justify-between annotation !text-[0.62rem] mt-1">
                                    <span>{d.low}</span><span>{d.high}</span>
                                </div>
                            </th>
                            <td className="text-right pr-4 figure-num !text-[1.5rem]">
                                {score !== null ? score : <span className="annotation !text-[0.8rem] italic" title="Not measurable from the available text">n/a</span>}
                            </td>
                            <td className="dek-sm">{dimensions.explanations[d.key] ?? <span className="annotation italic">No explanation recorded.</span>}</td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}
