'use client';
import { useEffect, useState } from 'react';

interface SurveyRow { id: number; code_report: string; date_survey: string; site_name: string; vessel_name: string; surveyor_name: string; sample_type: string; total_sample: number; }
interface FormData { id_vessel: string; id_site: string; date_survey: string; sample_type: string; total_sample: string; packages_number: string; }

export default function SurveyPage() {
    const [rows, setRows] = useState<SurveyRow[]>([]);
    const [search, setSearch] = useState('');
    const [tab, setTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [alert, setAlert] = useState<{ type: string; msg: string } | null>(null);
    const [form, setForm] = useState<FormData>({
        id_vessel: '', id_site: '', date_survey: new Date().toISOString().slice(0, 10),
        sample_type: 'Field Survey', total_sample: '0', packages_number: '0',
    });

    function load() {
        setLoading(true);
        fetch('/api/survey').then(r => r.json()).then(d => setRows(Array.isArray(d) ? d : [])).catch(() => { }).finally(() => setLoading(false));
    }
    useEffect(load, []);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault(); setSaving(true); setAlert(null);
        try {
            const res = await fetch('/api/survey', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, total_sample: Number(form.total_sample), packages_number: Number(form.packages_number) }) });
            const data = await res.json();
            if (res.ok) { setAlert({ type: 'success', msg: `✅ Survey ${data.doc_no} berhasil dibuat.` }); load(); setTab(0); }
            else { setAlert({ type: 'error', msg: `❌ ${data.error || 'Gagal menyimpan'}` }); }
        } catch { setAlert({ type: 'error', msg: '❌ Koneksi gagal' }); }
        finally { setSaving(false); }
    }

    const filtered = rows.filter(r =>
        !search ||
        (r.code_report || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.site_name || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.vessel_name || '').toLowerCase().includes(search.toLowerCase())
    );

    const latest = rows[0]?.date_survey ? new Date(rows[0].date_survey).toLocaleDateString('id-ID', { dateStyle: 'medium' }) : '—';

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">📋</div>
                <div>
                    <div className="page-header-title">Laporan Survei Harian</div>
                    <div className="page-header-subtitle">Field survey reports &amp; documentation</div>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid-3" style={{ marginBottom: 24 }}>
                {[
                    { l: 'Total Laporan', v: rows.length, c: '#38bdf8' },
                    { l: 'Survei Terbaru', v: latest, c: '#22c55e' },
                    { l: 'Sample Types', v: [...new Set(rows.map(r => r.sample_type))].length, c: '#818cf8' },
                ].map(m => (
                    <div key={m.l} className="metric-card" style={{ '--accent-color': m.c } as React.CSSProperties}>
                        <div className="metric-glow" />
                        <div className="metric-label">{m.l}</div>
                        <div className="metric-value" style={{ fontSize: '1.4rem' }}>{m.v}</div>
                    </div>
                ))}
            </div>

            {/* Tabs */}
            <div className="tab-list">
                {['📜 Daftar Survey', '➕ Buat Survey'].map((t, i) => (
                    <button key={t} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
                ))}
            </div>

            {tab === 0 && (
                <div className="card">
                    {alert && <div className={`alert alert-${alert.type === 'success' ? 'success' : 'error'}`} style={{ marginBottom: 12 }}>{alert.msg}</div>}
                    <div className="search-wrap" style={{ marginBottom: 16 }}>
                        <span className="search-icon">🔍</span>
                        <input className="search-input" placeholder="Cari kode, site, atau kapal..." value={search} onChange={e => setSearch(e.target.value)} />
                    </div>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}><div className="spinner" style={{ width: 22, height: 22, margin: '0 auto 8px' }} />Memuat...</div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table className="data-table">
                                <thead><tr>
                                    <th>Kode</th><th>Tanggal</th><th>Site</th><th>Kapal</th><th>Surveyor</th><th>Tipe</th><th>Sample</th>
                                </tr></thead>
                                <tbody>
                                    {filtered.length === 0
                                        ? <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--muted)' }}>Belum ada laporan survei</td></tr>
                                        : filtered.map(r => (
                                            <tr key={r.id}>
                                                <td><strong>{r.code_report}</strong></td>
                                                <td style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>{r.date_survey ? new Date(r.date_survey).toLocaleDateString('id-ID', { dateStyle: 'medium' }) : '—'}</td>
                                                <td>{r.site_name || '—'}</td>
                                                <td>{r.vessel_name || '—'}</td>
                                                <td>{r.surveyor_name || '—'}</td>
                                                <td><span className="badge badge-blue">{r.sample_type || '—'}</span></td>
                                                <td>{r.total_sample ?? '—'}</td>
                                            </tr>
                                        ))
                                    }
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {tab === 1 && (
                <div className="card" style={{ maxWidth: 700 }}>
                    <div className="card-title">✏️ Buat Laporan Survey Baru</div>
                    {alert && <div className={`alert alert-${alert.type === 'success' ? 'success' : 'error'}`}>{alert.msg}</div>}
                    <form onSubmit={handleSubmit}>
                        <div className="grid-2">
                            <div>
                                <div className="form-group">
                                    <label className="form-label">ID Kapal *</label>
                                    <input className="form-input" placeholder="e.g. VSL-001" value={form.id_vessel} onChange={e => setForm({ ...form, id_vessel: e.target.value })} required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">ID Site *</label>
                                    <input className="form-input" placeholder="e.g. SITE-001" value={form.id_site} onChange={e => setForm({ ...form, id_site: e.target.value })} required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Tanggal Survei</label>
                                    <input className="form-input" type="date" value={form.date_survey} onChange={e => setForm({ ...form, date_survey: e.target.value })} />
                                </div>
                            </div>
                            <div>
                                <div className="form-group">
                                    <label className="form-label">Tipe Sample</label>
                                    <select className="form-select" value={form.sample_type} onChange={e => setForm({ ...form, sample_type: e.target.value })}>
                                        {['Field Survey', 'Vibrocore', 'Grab Sample', 'Sediment Core', 'Water Sample'].map(t => <option key={t}>{t}</option>)}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Jumlah Sample</label>
                                    <input className="form-input" type="number" min="0" value={form.total_sample} onChange={e => setForm({ ...form, total_sample: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Jumlah Paket</label>
                                    <input className="form-input" type="number" min="0" value={form.packages_number} onChange={e => setForm({ ...form, packages_number: e.target.value })} />
                                </div>
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary btn-full" disabled={saving} style={{ marginTop: 8 }}>
                            {saving ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Menyimpan...</> : '💾 Simpan Laporan'}
                        </button>
                    </form>
                </div>
            )}
        </>
    );
}
