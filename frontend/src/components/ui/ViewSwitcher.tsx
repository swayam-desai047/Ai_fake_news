'use client';

import React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Radio, Layers, Sparkles } from 'lucide-react';

export default function ViewSwitcher() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const currentView = searchParams.get('view') || 'feed';

    const switchView = (newView: 'feed' | 'comparison') => {
        const params = new URLSearchParams(searchParams.toString());
        if (newView === 'feed') {
            params.delete('view');
        } else {
            params.set('view', 'comparison');
        }
        router.push(`/?${params.toString()}`);
    };

    return (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-6 p-2 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
            <div className="flex items-center gap-1.5 w-full sm:w-auto">
                <button
                    onClick={() => switchView('feed')}
                    className={`flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all w-1/2 sm:w-auto ${
                        currentView !== 'comparison'
                            ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white shadow-lg shadow-cyan-500/25'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                >
                    <Radio size={14} className={currentView !== 'comparison' ? 'animate-pulse' : ''} />
                    <span>Live Intelligence Feed</span>
                </button>

                <button
                    onClick={() => switchView('comparison')}
                    className={`flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all w-1/2 sm:w-auto ${
                        currentView === 'comparison'
                            ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-lg shadow-violet-500/25'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                >
                    <Layers size={14} className={currentView === 'comparison' ? 'text-cyan-300' : ''} />
                    <span>Cross-Source Comparison</span>
                    <span className="hidden sm:inline-block px-1.5 py-0.2 rounded text-[10px] bg-cyan-400/20 text-cyan-300 border border-cyan-400/30">
                        Multi-Source
                    </span>
                </button>
            </div>

            <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 pr-3">
                <Sparkles size={13} className="text-cyan-400" />
                <span>
                    {currentView === 'comparison'
                        ? 'Analyzing framing & tone divergence across competing newsrooms'
                        : 'Real-time verified stream with 8D credibility analysis'}
                </span>
            </div>
        </div>
    );
}
