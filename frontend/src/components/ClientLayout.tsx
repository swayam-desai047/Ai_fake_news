'use client';

import React, { useState, useEffect } from 'react';
import NameAuthModal from '@/components/ui/NameAuthModal';

interface ClientLayoutProps {
    children: React.ReactNode;
}

export const READER_STORAGE_KEY = 'ai_news_user';

/**
 * Keeps the existing name-based reader sign-in. The page renders immediately (no blank
 * loading screen); the register card appears over it only when no reader name is stored.
 */
export default function ClientLayout({ children }: ClientLayoutProps) {
    const [user, setUser] = useState<string | null>(null);
    const [checked, setChecked] = useState(false);

    useEffect(() => {
        let stored: string | null = null;
        try {
            stored = localStorage.getItem(READER_STORAGE_KEY);
        } catch {
            stored = null;
        }
        // Reading browser storage is only possible after mount.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (stored) setUser(stored);
        setChecked(true);
    }, []);

    const showRegister = checked && !user;

    return (
        <>
            <div data-user={user || ''} inert={showRegister || undefined}>
                {children}
            </div>
            {showRegister && <NameAuthModal onAuthenticated={setUser} />}
        </>
    );
}
