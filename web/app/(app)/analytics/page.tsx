'use client';
import { useEffect, useState } from 'react';
import {
    ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
    ScatterChart, Scatter, ZAxis
} from 'recharts';

interface AnalyticsData {
    monthly_revenue: { month: string; revenue: number }[];
    forecast: { month: string; revenue: number; isForecast: boolean }[];
    logistics: { destination: string; total_trips: number; avg_delay_hours: number }[];
}

function formatRev(v: number) { if (v >= 1e9) return `${(v / 1e9).toFixed(1)}M`; if (v >= 1e6) return `${(v / 1e6).toFixed(0)}Jt`; return String(v); }

export default function AnalyticsPage() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/analytics').then(r => r.json()).then(setData).catch(() => { }).finally(() => setLoading(false));
    }, []);

    // Merge actual + forecast for combined chart
    const chartData = data ? [
        ...data.monthly_revenue.map(d => ({ ...d, type: 'actual' })),
        ...data.forecast.map(d => ({ ...d, type: 'forecast' })),
    ] : [];

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">📈</div>
                <div>
                    <div className="page-header-title">Pusat Analitik</div>
                    <div className="page-header-subtitle">Financial intelligence &amp; operational analytics</div>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: 60, color: 'var(--muted)' }}>
                    <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto 12px' }} />Memuat analitik...
                </div>
            ) : (
                <>
                    {/* Revenue Forecast Chart */}
                    <div className="card" style={{ marginBottom: 20 }}>
                        <div className="card-title">💹 Proyeksi Pendapatan — AI 6 Bulan ke Depan</div>
                        <ResponsiveContainer width="100%" height={340}>
                            <ComposedChart data={chartData} margin={{ left: -10 }}>
                                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                                <XAxis dataKey="month" tick={{ fill: '#8ba3c0', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fill: '#8ba3c0', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={formatRev} />
                                <Tooltip
                                    contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text)' }}
                                    formatter={(v: number) => [`Rp ${v.toLocaleString('id-ID')}`, 'Pendapatan']}
                                />
                                <Legend formatter={(v) => <span style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{v}</span>} />
                                <Bar dataKey="revenue" fill="#0ea5e9" radius={[4, 4, 0, 0]} name="Aktual" />
                                <Line
                                    type="monotone" dataKey="revenue" stroke="#818cf8" strokeWidth={2.5}
                                    strokeDasharray="6 3" dot={{ fill: '#818cf8', r: 4 }} name="Proyeksi AI"
                                    data={chartData.filter(d => d.type === 'forecast')}
                                />
                            </ComposedChart>
                        </ResponsiveContainer>
                        <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginTop: 8 }}>
                            🧠 <strong>Model:</strong> Regresi Linear — proyeksi berdasarkan tren 12 bulan terakhir
                        </div>
                    </div>

                    <div className="grid-2-1" style={{ gap: 20 }}>
                        {/* Logistics Performance */}
                        <div className="card">
                            <div className="card-title">🚚 Kinerja Logistik</div>
                            {data?.logistics && data.logistics.length > 0 ? (
                                <div style={{ overflowX: 'auto' }}>
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Destinasi</th>
                                                <th>Total Trip</th>
                                                <th>Avg Delay (Jam)</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.logistics.map((row, i) => {
                                                const delay = Number(row.avg_delay_hours ?? 0);
                                                const cls = delay > 24 ? 'badge-rose' : delay > 8 ? 'badge-amber' : 'badge-green';
                                                const label = delay > 24 ? 'Kritis' : delay > 8 ? 'Terlambat' : 'On Time';
                                                return (
                                                    <tr key={i}>
                                                        <td>{row.destination}</td>
                                                        <td>{row.total_trips}</td>
                                                        <td>{delay.toFixed(1)}</td>
                                                        <td><span className={`badge ${cls}`}>{label}</span></td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <div className="empty-state"><div className="empty-state-title">Tidak ada data logistik</div></div>
                            )}
                        </div>

                        {/* AI Insights */}
                        <div className="card">
                            <div className="card-title">🧠 AI Insights</div>
                            {[
                                { type: 'info', title: 'Proyeksi Aktif', desc: 'Model regresi linear memproyeksikan 6 bulan ke depan berdasarkan tren historis.' },
                                { type: 'positive', title: 'Data Terintegrasi', desc: 'Semua data diambil langsung dari database PostgreSQL produksi secara real-time.' },
                                { type: 'info', title: 'Korelasi Tersedia', desc: 'Data siklus pendapatan tersedia untuk analisis korelasi Pearson.' },
                            ].map((ins, i) => {
                                const cfg: { bg: string; border: string; accent: string; icon: string } = {
                                    info: { bg: 'rgba(14,165,233,0.08)', border: 'rgba(14,165,233,0.25)', accent: '#0ea5e9', icon: '🤖' },
                                    positive: { bg: 'rgba(34,197,94,0.08)', border: 'rgba(34,197,94,0.25)', accent: '#22c55e', icon: '✅' },
                                    critical: { bg: 'rgba(244,63,94,0.08)', border: 'rgba(244,63,94,0.25)', accent: '#f43f5e', icon: '🚨' },
                                    warning: { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)', accent: '#f59e0b', icon: '⚠️' },
                                }[ins.type] ?? { bg: 'rgba(14,165,233,0.08)', border: 'rgba(14,165,233,0.25)', accent: '#0ea5e9', icon: '🤖' };
                                return (
                                    <div key={i} className="insight-banner animate-slide" style={{ background: cfg.bg, borderColor: cfg.border, borderLeftColor: cfg.accent }}>
                                        <div className="insight-icon">{cfg.icon}</div>
                                        <div>
                                            <div className="insight-title">{ins.title}</div>
                                            <div className="insight-desc">{ins.desc}</div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
