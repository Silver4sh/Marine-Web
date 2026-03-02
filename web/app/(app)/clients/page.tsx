'use client';
import { useEffect, useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ZAxis, ResponsiveContainer, Cell } from 'recharts';

interface Client {
    code_client: string; name: string; industry: string; region: string;
    status: string; total_orders: number; ltv: number;
    churn_risk?: string; projects_active?: number;
}

const CHURN_COLORS: { [k: string]: string } = { Rendah: '#22c55e', Menengah: '#f59e0b', Tinggi: '#f43f5e' };

function enrichClients(clients: Client[]): Client[] {
    return clients.map(c => ({
        ...c,
        projects_active: c.total_orders,
        ltv: Number(c.ltv),
        churn_risk: c.total_orders >= 4 ? 'Rendah' : c.total_orders >= 2 ? 'Menengah' : 'Tinggi',
    }));
}

export default function ClientsPage() {
    const [raw, setRaw] = useState<Client[]>([]);
    const [clients, setClients] = useState<Client[]>([]);
    const [search, setSearch] = useState('');
    const [sort, setSort] = useState('ltv');
    const [tab, setTab] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/clients').then(r => r.json()).then(d => {
            const enriched = enrichClients(Array.isArray(d) ? d : []);
            setRaw(enriched); setClients(enriched);
        }).catch(() => { }).finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        let filtered = [...raw];
        if (search) filtered = filtered.filter(c => c.name.toLowerCase().includes(search.toLowerCase()) || c.industry.toLowerCase().includes(search.toLowerCase()));
        if (sort === 'ltv') filtered.sort((a, b) => b.ltv - a.ltv);
        if (sort === 'orders') filtered.sort((a, b) => b.total_orders - a.total_orders);
        if (sort === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name));
        setClients(filtered);
    }, [search, sort, raw]);

    const maxLtv = Math.max(...raw.map(c => c.ltv), 1);
    const atRisk = raw.filter(c => c.churn_risk === 'Tinggi').length;
    const avgOrders = raw.length ? (raw.reduce((s, c) => s + c.total_orders, 0) / raw.length).toFixed(1) : '0';
    const premiumSum = raw.filter(c => c.ltv > 3_000_000_000).reduce((s, c) => s + c.ltv, 0);

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">👥</div>
                <div>
                    <div className="page-header-title">Portofolio Klien Strategis</div>
                    <div className="page-header-subtitle">Advanced CRM analytics &amp; distribution</div>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: 60, color: 'var(--muted)' }}><div className="spinner" style={{ width: 28, height: 28, margin: '0 auto 12px' }} />Memuat klien...</div>
            ) : (
                <>
                    {/* Metric Cards */}
                    <div className="metric-grid" style={{ marginBottom: 24 }}>
                        {[
                            { l: 'Total Klien', v: raw.length, d: `${raw.filter(c => c.status === 'Active').length} aktif`, c: '#38bdf8', icon: '👥' },
                            { l: 'Rata-rata Proyek', v: avgOrders, d: 'Beban operasional', c: '#fbbf24', icon: '📊' },
                            { l: 'Pipeline Premium', v: `Rp ${(premiumSum / 1e9).toFixed(1)}M`, d: 'Akun prioritas', c: '#2dd4bf', icon: '💎' },
                            { l: 'Risiko Churn', v: atRisk, d: 'Perlu atensi segera', c: '#f43f5e', icon: '⚠️' },
                        ].map(m => (
                            <div key={m.l} className="metric-card" style={{ '--accent-color': m.c } as React.CSSProperties}>
                                <div className="metric-glow" />
                                <div className="metric-label">{m.l}</div>
                                <div className="metric-value">{m.v}</div>
                                <div className="metric-delta">{m.icon} {m.d}</div>
                            </div>
                        ))}
                    </div>

                    {/* Tabs */}
                    <div className="tab-list">
                        {['🚀 Matriks Nilai', '📋 Direktori'].map((t, i) => (
                            <button key={t} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
                        ))}
                    </div>

                    {tab === 0 && (
                        <div className="grid-2-1" style={{ gap: 20 }}>
                            <div className="card">
                                <div className="card-title">📊 Scatter Matrix — Proyek vs. LTV</div>
                                {raw.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={350}>
                                        <ScatterChart>
                                            <XAxis dataKey="total_orders" name="Proyek Aktif" label={{ value: 'Proyek Aktif', position: 'insideBottom', offset: -5, fill: '#8ba3c0', fontSize: 12 }} tick={{ fill: '#8ba3c0', fontSize: 11 }} />
                                            <YAxis dataKey="ltv" name="LTV" tickFormatter={v => v >= 1e9 ? `${(v / 1e9).toFixed(0)}M` : v >= 1e6 ? `${(v / 1e6).toFixed(0)}Jt` : v} tick={{ fill: '#8ba3c0', fontSize: 11 }} />
                                            <ZAxis dataKey="ltv" range={[60, 400]} />
                                            <Tooltip
                                                contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10 }}
                                                formatter={(v: number, n: string) => [n === 'LTV' ? `Rp ${v.toLocaleString('id-ID')}` : v, n]}
                                                cursor={{ strokeDasharray: '3 3' }}
                                            />
                                            <Scatter data={raw} name="Klien">
                                                {raw.map((c, i) => (
                                                    <Cell key={i} fill={CHURN_COLORS[c.churn_risk ?? 'Menengah']} fillOpacity={0.8} />
                                                ))}
                                            </Scatter>
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="empty-state"><div className="empty-state-title">Tidak ada data klien</div></div>
                                )}
                            </div>
                            <div className="card">
                                <div className="card-title">💡 Audit Strategi</div>
                                {[
                                    { type: 'info', t: 'Mitra Kunci', d: 'Klien dengan banyak proyek aktif dan LTV tinggi adalah mitra utama yang harus dipertahankan.' },
                                    { type: 'warning', t: 'Potensi Upsell', d: 'Klien dengan LTV tinggi tetapi sedikit proyek aktif memiliki potensi pengembangan layanan.' },
                                    { type: 'critical', t: 'Churn ', d: `${atRisk} klien dengan aktivitas rendah memerlukan tindak lanjut segera.` },
                                ].map((ins, i) => {
                                    const cfg: { bg: string; border: string; accent: string; icon: string } = {
                                        info: { bg: 'rgba(14,165,233,0.08)', border: 'rgba(14,165,233,0.25)', accent: '#0ea5e9', icon: '🤖' },
                                        warning: { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)', accent: '#f59e0b', icon: '⚠️' },
                                        critical: { bg: 'rgba(244,63,94,0.08)', border: 'rgba(244,63,94,0.25)', accent: '#f43f5e', icon: '🚨' },
                                    }[ins.type]!;
                                    return (
                                        <div key={i} className="insight-banner" style={{ background: cfg.bg, borderColor: cfg.border, borderLeftColor: cfg.accent, marginBottom: 8 }}>
                                            <div className="insight-icon">{cfg.icon}</div>
                                            <div><div className="insight-title">{ins.t}</div><div className="insight-desc">{ins.d}</div></div>
                                        </div>
                                    );
                                })}
                                <div style={{ marginTop: 12 }}>
                                    <div style={{ marginBottom: 8, fontSize: '0.8rem', fontWeight: 600, color: 'var(--muted)' }}>LEGENDA RISIKO CHURN</div>
                                    {Object.entries(CHURN_COLORS).map(([k, c]) => (
                                        <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
                                            <div style={{ width: 10, height: 10, borderRadius: '50%', background: c }} />
                                            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{k}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {tab === 1 && (
                        <div className="card">
                            <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
                                <div className="search-wrap" style={{ flex: 1 }}>
                                    <span className="search-icon">🔍</span>
                                    <input className="search-input" placeholder="Cari nama klien atau industri..." value={search} onChange={e => setSearch(e.target.value)} />
                                </div>
                                <select className="form-select" style={{ width: 220 }} value={sort} onChange={e => setSort(e.target.value)}>
                                    <option value="ltv">LTV (Tinggi–Rendah)</option>
                                    <option value="orders">Proyek (Tinggi–Rendah)</option>
                                    <option value="name">Nama (A–Z)</option>
                                </select>
                            </div>
                            <div style={{ overflowX: 'auto' }}>
                                <table className="data-table">
                                    <thead><tr>
                                        <th>Nama Klien</th><th>Industri</th><th>Region</th>
                                        <th>Proyek</th><th>LTV (IDR)</th><th>Churn Risk</th>
                                    </tr></thead>
                                    <tbody>
                                        {clients.length === 0 ? (
                                            <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>Tidak ada hasil</td></tr>
                                        ) : clients.map(c => (
                                            <tr key={c.code_client}>
                                                <td><strong>{c.name}</strong></td>
                                                <td><span className="badge badge-blue">{c.industry}</span></td>
                                                <td style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>{c.region}</td>
                                                <td>{c.total_orders}</td>
                                                <td>
                                                    <div>Rp {c.ltv.toLocaleString('id-ID')}</div>
                                                    <div className="progress-bar" style={{ marginTop: 4 }}>
                                                        <div className="progress-fill" style={{ width: `${Math.round((c.ltv / maxLtv) * 100)}%` }} />
                                                    </div>
                                                </td>
                                                <td><span className={`badge ${c.churn_risk === 'Tinggi' ? 'badge-rose' : c.churn_risk === 'Menengah' ? 'badge-amber' : 'badge-green'}`}>{c.churn_risk}</span></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}
        </>
    );
}
