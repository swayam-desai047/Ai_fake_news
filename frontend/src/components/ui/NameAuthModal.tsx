'use client';

import React, { useState } from 'react';

interface NameAuthModalProps {
    onAuthenticated: (name: string) => void;
}

/** The reader register: the existing name-only sign-in, set as a printed subscription card. */
export default function NameAuthModal({ onAuthenticated }: NameAuthModalProps) {
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const trimmedName = name.trim();
        if (!trimmedName) {
            setError('Please enter your name to continue.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const res = await fetch('/api/auth/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: trimmedName }),
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                setError(data.error || 'Something went wrong. Try again.');
                setLoading(false);
                return;
            }

            try {
                localStorage.setItem('ai_news_user', trimmedName);
            } catch {
                /* storage unavailable: the session still continues */
            }
            onAuthenticated(trimmedName);
        } catch {
            setError('Network error. Please try again.');
            setLoading(false);
        }
    };

    return (
        <div className="register-backdrop" role="dialog" aria-modal="true" aria-labelledby="register-title">
            <div className="register-card">
                <p className="kicker">Reader&rsquo;s register</p>
                <h1 id="register-title" className="font-[family-name:var(--font-display)] font-black text-[2.1rem] leading-none mt-3">
                    The Daily Signal
                </h1>
                <p className="masthead__tagline !mt-2">News, context and credibility.</p>
                <hr className="rule-double my-5" />
                <p className="dek-sm mb-5">
                    Sign the register with your name to open today&rsquo;s edition. No password is required.
                </p>

                <form onSubmit={handleSubmit} className="text-left">
                    <label htmlFor="reader-name" className="field-label">Your name</label>
                    <input
                        id="reader-name"
                        type="text"
                        value={name}
                        onChange={(e) => { setName(e.target.value); setError(''); }}
                        placeholder="e.g. A. Reader"
                        autoFocus
                        autoComplete="name"
                        maxLength={60}
                        className="field"
                        disabled={loading}
                        aria-invalid={Boolean(error)}
                        aria-describedby={error ? 'reader-error' : undefined}
                    />

                    {error && (
                        <p id="reader-error" role="alert" className="annotation !text-[var(--red)] mt-2">
                            {error}
                        </p>
                    )}

                    <button type="submit" disabled={loading || !name.trim()} className="btn w-full mt-6">
                        {loading ? 'Opening the edition…' : 'Open today’s edition'}
                    </button>
                </form>
            </div>
        </div>
    );
}
