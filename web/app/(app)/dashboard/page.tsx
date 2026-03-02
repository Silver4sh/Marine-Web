'use client';
import { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';

interface FleetData { total_vessels: number; operating: number; maintenance: number; idle: number; }
interface OrderData { total_orders: number; completed: number; on_progress: number; open: number; }
interface FinancialData { total_revenue: number; delta_revenue: number; monthly_revenue: { month: string; revenue: number }[]; }

function MetricCard({ label, value, delta, color, icon }:
    { label: string; value: string | number; delta: string; color: string; icon: string }) {
    return (
        <div className="metric-card" style={{ '--accent-color': color } as React.CSSProperties}>
            <div className="metric-glow" />
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
            <div className="metric-delta">{icon} {delta}</div>
        </div>
    );
}

const PIE_COLORS = ['#2dd4bf', '#f472b6', '#fbbf24'];

function formatRevenue(v: number) {
    if (v >= 1e9) return `Rp ${(v / 1e9).toFixed(1)}M`;
    if (v >= 1e6) return `Rp ${(v / 1e6).toFixed(1)}Jt`;
    return `Rp ${v.toLocaleString('id-ID')}`;
}

export default function DashboardPage() {
    const [fleet, setFleet] = useState<FleetData | null>(null);
    const [orders, setOrders] = useState<OrderData | null>(null);
    const [financial, setFinancial] = useState<FinancialData | null>(null);
    const [role, setRole] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const [s, f, o, fin] = await Promise.allSettled([
                fetch('/api/auth').then(r => r.json()),
                fetch('/api/fleet').then(r => r.json()),
                fetch('/api/orders').then(r => r.json()),
                fetch('/api/financial').then(r => r.json()),
            ]);
            if (s.status === 'fulfilled') setRole(s.value.role || '');
            if (f.status === 'fulfilled') setFleet(f.value);
            if (o.status === 'fulfilled') setOrders(o.value);
            if (fin.status === 'fulfilled') setFinancial(fin.value);
            setLoading(false);
        }
        load();
    }, []);

    const canViewFinancial = ['Admin', 'Finance', 'MarCom'].includes(role);

    const orderPieData = orders ? [
        { name: 'Selesai', value: orders.completed },
        { name: 'Berjalan', value: orders.on_progress },
        { name: 'Terbuka', value: orders.open },
    ] : [];

    const fleetHealth = fleet
        ? Math.round(((fleet.total_vessels - fleet.maintenance) / Math.max(fleet.total_vessels, 1)) * 100)
        : 0;

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">🏠</div>
                <div>
                    <div className="page-header-title">Monitoring</div>
                    <div className="page-header-subtitle">Real-time fleet &amp; operational overview</div>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '60px', color: 'var(--muted)' }}>
                    <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto 12px' }} />
                    <div>Memuat data...</div>
                </div>
            ) : (
                <>
                    {/* Metric Cards */}
                    <div className="metric-grid">
                        <MetricCard
                            label="Kapal Beroperasi"
                            value={fleet?.operating ?? 0}
                            delta={`${fleet?.maintenance ?? 0} dalam Perawatan`}
                            color="#f59e0b" icon="🚢"
                        />
                        <MetricCard
                            label="Pesanan Tertunda"
                            value={(orders?.on_progress ?? 0) + (orders?.open ?? 0)}
                            delta="Perlu Tindakan"
                            color="#f472b6" icon="📦"
                        />
                        {canViewFinancial ? (
                            <MetricCard
                                label="Pendapatan Bulan Ini"
                                value={formatRevenue(financial?.total_revenue ?? 0)}
                                delta={`${(financial?.delta_revenue ?? 0) >= 0 ? '+' : ''}${financial?.delta_revenue ?? 0}% vs bulan lalu`}
                                color={(financial?.delta_revenue ?? 0) >= 0 ? '#0ea5e9' : '#f43f5e'} icon="💰"
                            />
                        ) : (
                            <MetricCard
                                label="Kesehatan Armada"
                                value={`${fleetHealth}%`}
                                delta="Armada Operasional"
                                color="#38bdf8" icon="⚓"
                            />
                        )}
                        <MetricCard
                            label="Task Selesai"
                            value={orders?.completed ?? 0}
                            delta="Total diselesaikan"
                            color="#2dd4bf" icon="✅"
                        />
                    </div>

                    {/* Main Content Grid */}
                    <div className="grid-2-1" style={{ gap: 24 }}>
                        {/* Chart */}
                        <div className="card">
                            <div className="card-title">
                                📊 {canViewFinancial ? 'Arus Pendapatan Bulanan' : 'Distribusi Pesanan'}
                            </div>
                            {canViewFinancial && financial?.monthly_revenue?.length ? (
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={financial.monthly_revenue} margin={{ left: -10 }}>
                                        <XAxis dataKey="month" tick={{ fill: '#8ba3c0', fontSize: 11 }} axisLine={false} tickLine={false} />
                                        <YAxis tick={{ fill: '#8ba3c0', fontSize: 11 }} axisLine={false} tickLine={false}
                                            tickFormatter={v => v >= 1e9 ? `${(v / 1e9).toFixed(0)}M` : v >= 1e6 ? `${(v / 1e6).toFixed(0)}Jt` : String(v)}
                                        />
                                        <Tooltip
                                            contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text)' }}
                                            formatter={(v: number) => [formatRevenue(v), 'Pendapatan']}
                                        />
                                        <Bar dataKey="revenue" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie data={orderPieData} dataKey="value" cx="50%" cy="50%" innerRadius={70} outerRadius={110}>
                                            {orderPieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                                        </Pie>
                                        <Legend formatter={(v) => <span style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>{v}</span>} />
                                        <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10 }} />
                                    </PieChart>
                                </ResponsiveContainer>
                            )}
                        </div>

                        {/* Fleet Summary */}
                        <div className="card">
                            <div className="card-title">🚢 Ringkasan Armada</div>
                            {fleet && [
                                { label: 'Beroperasi', count: fleet.operating, color: '#22c55e' },
                                { label: 'Idle', count: fleet.idle, color: '#8ba3c0' },
                                { label: 'Perawatan', count: fleet.maintenance, color: '#f59e0b' },
                            ].map(row => (
                                <div key={row.label} style={{ marginBottom: 16 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{row.label}</span>
                                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: row.color }}>{row.count}</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{
                                            width: `${Math.round((row.count / Math.max(fleet.total_vessels, 1)) * 100)}%`,
                                            background: row.color
                                        }} />
                                    </div>
                                </div>
                            ))}

                            <div className="divider" />
                            <div className="card-title" style={{ marginBottom: 12 }}>⚡ Tindakan Cepat</div>
                            {['Admin', 'Operations'].includes(role) && (
                                <a href="/map" className="btn btn-ghost btn-full btn-sm" style={{ marginBottom: 8 }}>
                                    🗺️ Buka Peta Kapal
                                </a>
                            )}
                            <a href="/survey" className="btn btn-ghost btn-full btn-sm">
                                📋 Buat Survey Baru
                            </a>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
