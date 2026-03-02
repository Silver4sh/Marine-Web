'use client';
import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface Buoy { code_buoy: string; status: string; location: string; last_update: string; latitude: number; longitude: number; }
interface SensorRow { created_at: string; salinitas: number; turbidity: number; oxygen: number; density: number; current: number; tide: number; }

const STATUS_COLOR: Record<string, string> = {
    Active: '#22c55e', Inactive: '#8ba3c0', MTC: '#f59e0b',
};

function BuoyCard({ buoy, onDetail }: { buoy: Buoy; onDetail: (b: Buoy) => void }) {
    const color = STATUS_COLOR[buoy.status] ?? '#8ba3c0';
    const bg = buoy.status === 'Active'
        ? 'linear-gradient(145deg, rgba(34,197,94,0.1), rgba(10,16,32,0.6))'
        : buoy.status === 'MTC'
            ? 'linear-gradient(145deg, rgba(245,158,11,0.1), rgba(10,16,32,0.6))'
            : 'linear-gradient(145deg, rgba(139,163,192,0.07), rgba(10,16,32,0.6))';

    const lastUpd = buoy.last_update ? new Date(buoy.last_update).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'short' }) : '—';

    return (
        <div className="buoy-card" style={{ background: bg, borderColor: `${color}30` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                <span style={{ fontFamily: 'var(--font-disp)', fontWeight: 700, fontSize: '0.9rem' }}>📡 {buoy.code_buoy}</span>
                <span className={`badge badge-${buoy.status === 'Active' ? 'green' : buoy.status === 'MTC' ? 'amber' : 'gray'}`}>{buoy.status}</span>
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginBottom: 2 }}>📍 {buoy.location || 'N/A'}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--muted-2)', marginBottom: 12 }}>🕐 {lastUpd}</div>
            <button className="btn btn-ghost btn-sm btn-full" onClick={() => onDetail(buoy)}>
                Detail 🔍
            </button>
        </div>
    );
}

function SensorChart({ data, keys, colors }: { data: SensorRow[]; keys: string[]; colors: string[] }) {
    const cleaned = data.map(d => ({ ...d, ts: new Date(d.created_at).toLocaleDateString('id-ID') }));
    return (
        <ResponsiveContainer width="100%" height={200}>
            <LineChart data={cleaned} margin={{ left: -15, right: 5 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="ts" tick={{ fill: '#8ba3c0', fontSize: 10 }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fill: '#8ba3c0', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text)' }} />
                {keys.map((k, i) => <Line key={k} type="monotone" dataKey={k} stroke={colors[i]} dot={false} strokeWidth={2} />)}
            </LineChart>
        </ResponsiveContainer>
    );
}

const TABS = ['🔥 Buoy Fleet', '📊 Detail Sensor'];

export default function EnvironmentPage() {
    const [buoys, setBuoys] = useState<Buoy[]>([]);
    const [activeTab, setActiveTab] = useState(0);
    const [detail, setDetail] = useState<Buoy | null>(null);
    const [sensorData, setSensorData] = useState<SensorRow[]>([]);
    const [loadingSensor, setLoadingSensor] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/environment/buoys').then(r => r.json()).then(d => { setBuoys(d); setLoading(false); }).catch(() => setLoading(false));
    }, []);

    async function loadDetail(b: Buoy) {
        setDetail(b); setActiveTab(1); setLoadingSensor(true);
        const rows = await fetch(`/api/environment/sensor/${b.code_buoy}`).then(r => r.json()).catch(() => []);
        setSensorData(rows); setLoadingSensor(false);
    }

    const total = buoys.length;
    const active = buoys.filter(b => b.status === 'Active').length;
    const mtc = buoys.filter(b => b.status === 'MTC').length;

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">🌊</div>
                <div>
                    <div className="page-header-title">Enviro Control</div>
                    <div className="page-header-subtitle">Marine environmental monitoring &amp; buoy telemetry</div>
                </div>
            </div>

            {/* Summary Metrics */}
            <div className="grid-3" style={{ marginBottom: 24 }}>
                {[{ l: 'Total Buoy', v: total, c: '#38bdf8' }, { l: 'Buoy Aktif', v: active, c: '#22c55e' }, { l: 'Perawatan', v: mtc, c: '#f59e0b' }].map(m => (
                    <div key={m.l} className="metric-card" style={{ '--accent-color': m.c } as React.CSSProperties}>
                        <div className="metric-glow" />
                        <div className="metric-label">{m.l}</div>
                        <div className="metric-value">{m.v}</div>
                    </div>
                ))}
            </div>

            {/* Tabs */}
            <div className="tab-list">
                {TABS.map((t, i) => (
                    <button key={t} className={`tab-btn ${activeTab === i ? 'active' : ''}`} onClick={() => setActiveTab(i)}>{t}</button>
                ))}
            </div>

            {activeTab === 0 && (
                loading ? (
                    <div style={{ textAlign: 'center', padding: 48, color: 'var(--muted)' }}>
                        <div className="spinner" style={{ width: 28, height: 28, margin: '0 auto 12px' }} />Memuat buoy...
                    </div>
                ) : buoys.length === 0 ? (
                    <div className="empty-state"><div className="empty-state-icon">📡</div><div className="empty-state-title">Belum ada data buoy</div></div>
                ) : (
                    <div className="grid-4">
                        {buoys.map(b => <BuoyCard key={b.code_buoy} buoy={b} onDetail={loadDetail} />)}
                    </div>
                )
            )}

            {activeTab === 1 && (
                <div>
                    {!detail ? (
                        <div className="empty-state"><div className="empty-state-icon">🔍</div><div className="empty-state-title">Pilih buoy untuk melihat detail sensor</div><div className="empty-state-desc">Klik tombol &quot;Detail&quot; pada card buoy</div></div>
                    ) : (
                        <div className="card animate-slide">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                                <div>
                                    <div style={{ fontFamily: 'var(--font-disp)', fontWeight: 800, fontSize: '1.1rem' }}>📡 {detail.code_buoy}</div>
                                    <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>📍 {detail.location || 'N/A'}</div>
                                </div>
                                <button className="btn btn-ghost btn-sm" onClick={() => setDetail(null)}>✖ Tutup</button>
                            </div>
                            {loadingSensor ? (
                                <div style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}><div className="spinner" style={{ width: 24, height: 24, margin: '0 auto 8px' }} />Memuat data sensor...</div>
                            ) : sensorData.length === 0 ? (
                                <div className="empty-state"><div className="empty-state-title">Belum ada data historis sensor</div></div>
                            ) : (
                                <div className="grid-2">
                                    <div><div className="section-header"><span>🧂 Salinitas &amp; Kekeruhan</span></div><SensorChart data={sensorData} keys={['salinitas', 'turbidity']} colors={['#0ea5e9', '#f472b6']} /></div>
                                    <div><div className="section-header"><span>💨 Oksigen &amp; Densitas</span></div><SensorChart data={sensorData} keys={['oxygen', 'density']} colors={['#22c55e', '#818cf8']} /></div>
                                    <div><div className="section-header"><span>🌊 Arus (Current)</span></div><SensorChart data={sensorData} keys={['current']} colors={['#2dd4bf']} /></div>
                                    <div><div className="section-header"><span>🌊 Pasang Surut (Tide)</span></div><SensorChart data={sensorData} keys={['tide']} colors={['#f59e0b']} /></div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </>
    );
}
