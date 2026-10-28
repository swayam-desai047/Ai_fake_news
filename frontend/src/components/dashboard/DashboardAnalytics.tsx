'use client';

import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

/**
 * Editorial chart primitives for The News Intelligence Report: ink marks, hairline grids,
 * direct value labels and plain tooltips.
 */

const INK = '#171717';
const MUTED = '#626262';
const GRID = '#D8D6D0';
const TICK = { fill: MUTED, fontSize: 11, fontFamily: 'var(--font-sans)' };

export interface BarDatum {
    label: string;
    value: number;
    /** Only for status meanings (credibility risk); everything else is ink. */
    color?: string;
    note?: string;
}

function BarTooltip({ active, payload, unit }: { active?: boolean; payload?: { payload: BarDatum }[]; unit: string }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
        <div className="chart-tooltip">
            <strong>{d.label}</strong>: {d.value}{unit}
            {d.note && <div className="text-[var(--ink-2)]">{d.note}</div>}
        </div>
    );
}

/** Horizontal bar chart with a direct label on every bar (category counts are few). */
export function HorizontalBars({ data, unit = '', max, labelWidth = 110, ariaLabel }: {
    data: BarDatum[];
    unit?: string;
    max?: number;
    labelWidth?: number;
    ariaLabel: string;
}) {
    const height = Math.max(120, data.length * 34 + 28);
    return (
        <div style={{ height }} role="img" aria-label={ariaLabel}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} layout="vertical" margin={{ top: 4, right: 44, bottom: 4, left: 0 }} barCategoryGap={8}>
                    <CartesianGrid horizontal={false} stroke={GRID} strokeWidth={1} />
                    <XAxis type="number" domain={[0, max ?? 'auto']} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                    <YAxis type="category" dataKey="label" width={labelWidth} tick={{ ...TICK, fill: INK, fontWeight: 600 }} axisLine={{ stroke: INK }} tickLine={false} />
                    <Tooltip content={<BarTooltip unit={unit} />} cursor={{ fill: 'rgba(23,23,23,0.04)' }} />
                    <Bar dataKey="value" radius={[0, 2, 2, 0]} maxBarSize={18} animationDuration={800}>
                        {data.map(d => <Cell key={d.label} fill={d.color ?? INK} />)}
                        <LabelList dataKey="value" position="right" formatter={(v: unknown) => `${v}${unit}`} style={{ fill: INK, fontSize: 11, fontWeight: 600, fontFamily: 'var(--font-sans)' }} />
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

function TimeTooltip({ active, payload }: { active?: boolean; payload?: { payload: { label: string; count: number } }[] }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
        <div className="chart-tooltip">
            <strong>{d.label}</strong>
            <div>{d.count} {d.count === 1 ? 'report' : 'reports'} published</div>
        </div>
    );
}

/** Reports per hour of publication. */
export function Timeline({ data, ariaLabel }: { data: { label: string; tick: string; count: number }[]; ariaLabel: string }) {
    return (
        <div className="h-[240px]" role="img" aria-label={ariaLabel}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
                    <CartesianGrid vertical={false} stroke={GRID} strokeWidth={1} />
                    <XAxis dataKey="tick" tick={TICK} axisLine={{ stroke: INK }} tickLine={false} interval="preserveStartEnd" minTickGap={28} />
                    <YAxis tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip content={<TimeTooltip />} cursor={{ stroke: INK, strokeWidth: 1, strokeDasharray: '3 3' }} />
                    <Area type="monotone" dataKey="count" stroke={INK} strokeWidth={2} fill={INK} fillOpacity={0.07} activeDot={{ r: 4, fill: INK, stroke: '#FAF9F6', strokeWidth: 2 }} animationDuration={900} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
