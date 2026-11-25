'use client';

import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';
import { DIMENSIONS } from '@/lib/dimensions';
import type { DimensionScores } from '@/lib/types';

interface DimensionRadarChartProps {
    dimensions: DimensionScores;
    /** Optional second profile (e.g. edition average) drawn as a dashed outline. */
    comparison?: Partial<Record<keyof DimensionScores, number>> | null;
    comparisonLabel?: string;
}

interface Row {
    axis: string;
    label: string;
    score: number | null;
    comparison?: number;
    low: string;
    high: string;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: { payload: Row }[] }) {
    if (!active || !payload?.length) return null;
    const row = payload[0].payload;
    return (
        <div className="chart-tooltip">
            <strong>{row.label}</strong>: {row.score === null ? 'not scored' : `${row.score}/100`}
            {typeof row.comparison === 'number' && <div>Edition average: {row.comparison}</div>}
            <div className="text-[var(--ink-2)]">0 = {row.low} · 100 = {row.high}</div>
        </div>
    );
}

/** Eight-dimension profile in ink, with thin gridlines. Paired with the score table for exact values. */
export default function DimensionRadarChart({ dimensions, comparison, comparisonLabel = 'Edition average' }: DimensionRadarChartProps) {
    const data: Row[] = DIMENSIONS.map(d => ({
        axis: dimensions[d.key] === null ? `${d.short} (n/a)` : d.short,
        label: d.label,
        score: dimensions[d.key],
        comparison: comparison?.[d.key] as number | undefined,
        low: d.low,
        high: d.high,
    }));

    return (
        <figure className="chart-block m-0">
            <div className="h-[320px] sm:h-[360px]" role="img" aria-label={`Radar chart of eight dimension scores: ${data.map(d => `${d.label} ${d.score ?? 'not scored'}`).join(', ')}.`}>
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={data} outerRadius="72%" margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
                        <PolarGrid stroke="#D8D6D0" strokeWidth={1} />
                        <PolarAngleAxis
                            dataKey="axis"
                            tick={{ fill: '#171717', fontSize: 11, fontFamily: 'var(--font-sans)', fontWeight: 600 }}
                        />
                        <PolarRadiusAxis domain={[0, 100]} tickCount={5} angle={90} tick={{ fill: '#8a8883', fontSize: 9 }} axisLine={false} />
                        {comparison && (
                            <Radar
                                name={comparisonLabel}
                                dataKey="comparison"
                                stroke="#8a8883"
                                strokeDasharray="4 3"
                                strokeWidth={1.5}
                                fill="transparent"
                                isAnimationActive={false}
                            />
                        )}
                        <Radar
                            name="This report"
                            dataKey="score"
                            stroke="#171717"
                            strokeWidth={2}
                            fill="#171717"
                            fillOpacity={0.08}
                            dot={{ r: 3, fill: '#171717', strokeWidth: 0 }}
                            connectNulls
                            animationDuration={900}
                        />
                        <Tooltip content={<ChartTooltip />} cursor={false} />
                    </RadarChart>
                </ResponsiveContainer>
            </div>
            <figcaption className="annotation mt-1 flex flex-wrap gap-x-5 gap-y-1">
                <span className="inline-flex items-center gap-2"><span className="inline-block w-5 border-t-2 border-[var(--ink)]" />This report</span>
                {comparison && (
                    <span className="inline-flex items-center gap-2"><span className="inline-block w-5 border-t-2 border-dashed border-[var(--ink-3)]" />{comparisonLabel}</span>
                )}
            </figcaption>
        </figure>
    );
}
