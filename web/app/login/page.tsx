'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(''); setLoading(true);
        try {
            const res = await fetch('/api/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();
            if (!res.ok) { setError(data.error || 'Login gagal'); setLoading(false); return; }
            router.push('/dashboard');
        } catch {
            setError('Tidak dapat terhubung ke server'); setLoading(false);
        }
    }

    return (
        <div className="login-page">
            <div className="login-card animate-fade">
                <div className="login-logo">⚓ MarineOS</div>
                <p className="login-tagline">Marine Operations Intelligence Platform</p>

                {error && <div className="login-error">⚠️ {error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Username</label>
                        <input
                            id="username"
                            className="form-input"
                            type="text"
                            placeholder="Masukkan username"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            required
                            autoComplete="username"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            id="password"
                            className="form-input"
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>
                    <button
                        id="login-btn"
                        type="submit"
                        className="btn btn-primary btn-full"
                        style={{ marginTop: 8, padding: '12px' }}
                        disabled={loading}
                    >
                        {loading ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Masuk...</> : '🔐 Masuk ke Dashboard'}
                    </button>
                </form>

                <div style={{ marginTop: 24, padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 10, fontSize: '0.78rem', color: 'var(--muted)' }}>
                    <strong>Demo:</strong> Gunakan kredensial akun yang terdaftar di database.
                </div>
            </div>
        </div>
    );
}
