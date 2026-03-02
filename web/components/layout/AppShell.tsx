'use client';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useCallback } from 'react';

const ROLE_ADMIN = 'Admin';
const ROLE_OPERATIONS = 'Operations';
const ROLE_MARCOM = 'MarCom';
const ROLE_FINANCE = 'Finance';

const NAV_ITEMS = [
    { href: '/dashboard', icon: '🏠', label: 'Monitoring', roles: null },
    { href: '/environment', icon: '🌊', label: 'Lingkungan', roles: null },
    { href: '/map', icon: '🗺️', label: 'Peta Kapal', roles: [ROLE_ADMIN, ROLE_OPERATIONS] },
    { href: '/survey', icon: '📋', label: 'Survey', roles: [ROLE_ADMIN, ROLE_OPERATIONS] },
    { href: '/clients', icon: '👥', label: 'Klien', roles: [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE] },
    { href: '/analytics', icon: '📈', label: 'Analitik', roles: [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE] },
    { href: '/admin', icon: '👨‍💼', label: 'Admin Panel', roles: [ROLE_ADMIN] },
];

const ROLE_COLORS: Record<string, string> = {
    [ROLE_ADMIN]: '#818cf8',
    [ROLE_OPERATIONS]: '#22c55e',
    [ROLE_MARCOM]: '#f59e0b',
    [ROLE_FINANCE]: '#0ea5e9',
};

interface Props {
    session: { username: string; role: string; name: string };
    children: React.ReactNode;
}

export default function AppShell({ session, children }: Props) {
    const pathname = usePathname();
    const router = useRouter();
    const [loggingOut, setLoggingOut] = useState(false);

    const handleLogout = useCallback(async () => {
        setLoggingOut(true);
        await fetch('/api/auth', { method: 'DELETE' });
        router.push('/login');
    }, [router]);

    const visibleNav = NAV_ITEMS.filter(n => !n.roles || n.roles.includes(session.role));

    return (
        <div className="app-layout">
            {/* ── Sidebar ── */}
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <div className="brand-logo">⚓ MarineOS</div>
                    <div className="brand-tagline">Marine Operations Platform</div>
                </div>

                {/* User card */}
                <div className="user-card">
                    <div className="avatar">{(session.name || session.username)[0].toUpperCase()}</div>
                    <div>
                        <div className="user-name">{session.name || session.username}</div>
                        <div className="user-role" style={{ color: ROLE_COLORS[session.role] ?? '#8ba3c0' }}>
                            {session.role}
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav className="sidebar-nav">
                    <div className="nav-label" style={{ marginTop: 8 }}>Navigation</div>
                    {visibleNav.map(item => (
                        <a
                            key={item.href}
                            href={item.href}
                            className={`nav-btn ${pathname === item.href || pathname.startsWith(item.href + '/') ? 'active' : ''}`}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </a>
                    ))}

                    <div className="nav-divider" />

                    <button
                        id="logout-btn"
                        className="nav-btn"
                        onClick={handleLogout}
                        disabled={loggingOut}
                        style={{ color: 'var(--rose)' }}
                    >
                        <span className="nav-icon">🚪</span>
                        {loggingOut ? 'Keluar...' : 'Keluar'}
                    </button>
                </nav>

                {/* Footer */}
                <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', fontSize: '0.68rem', color: 'var(--muted-2)', textAlign: 'center' }}>
                    MarineOS v2.0 · 2025
                </div>
            </aside>

            {/* ── Main ── */}
            <main className="main-content">
                <div className="page-inner animate-fade">
                    {children}
                </div>
            </main>
        </div>
    );
}
