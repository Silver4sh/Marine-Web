'use client';
import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';

// Leaflet must be loaded client-side only
const MapContainer = dynamic(() => import('react-leaflet').then(m => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(m => m.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(m => m.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(m => m.Popup), { ssr: false });

interface Vessel {
    code_vessel: string; name: string; status: string;
    latitude: number; longitude: number; speed: number;
    last_update: string;
}

const STATUS_BADGE: Record<string, string> = {
    Operating: 'badge-green', Idle: 'badge-gray', Maintenance: 'badge-amber',
};

export default function MapPage() {
    const [vessels, setVessels] = useState<Vessel[]>([]);
    const [selected, setSelected] = useState<Vessel | null>(null);
    const [loading, setLoading] = useState(true);
    const mapRef = useRef<unknown>(null);

    useEffect(() => {
        // Fix leaflet icon in Next.js
        import('leaflet').then(L => {
            delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
            L.Icon.Default.mergeOptions({
                iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
                iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
                shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
            });
        });

        fetch('/api/vessels/positions').then(r => r.json()).then(d => {
            setVessels(Array.isArray(d) ? d : []);
        }).catch(() => { }).finally(() => setLoading(false));
    }, []);

    const center: [number, number] = vessels.length > 0
        ? [vessels[0].latitude || -2, vessels[0].longitude || 118]
        : [-2, 118];

    return (
        <>
            <div className="page-header">
                <div className="page-header-icon">🗺️</div>
                <div>
                    <div className="page-header-title">Peta Kapal</div>
                    <div className="page-header-subtitle">Real-time vessel tracking &amp; positioning</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 20, height: 'calc(100vh - 180px)' }}>
                {/* Vessel List Panel */}
                <div className="card" style={{ overflowY: 'auto', height: '100%', padding: 16 }}>
                    <div className="card-title">🚢 Armada ({vessels.length})</div>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: 32, color: 'var(--muted)' }}><div className="spinner" style={{ width: 22, height: 22, margin: '0 auto 8px' }} />Memuat...</div>
                    ) : vessels.length === 0 ? (
                        <div className="empty-state"><div className="empty-state-icon">🚢</div><div className="empty-state-title">Tidak ada data posisi kapal</div></div>
                    ) : (
                        vessels.map(v => (
                            <div key={v.code_vessel}
                                onClick={() => setSelected(v)}
                                style={{
                                    padding: '12px',
                                    borderRadius: 'var(--r-sm)',
                                    marginBottom: 8,
                                    border: `1px solid ${selected?.code_vessel === v.code_vessel ? 'var(--accent)' : 'var(--border)'}`,
                                    background: selected?.code_vessel === v.code_vessel ? 'rgba(14,165,233,0.08)' : 'transparent',
                                    cursor: 'pointer',
                                    transition: 'all 0.15s ease',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                    <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{v.name || v.code_vessel}</span>
                                    <span className={`badge ${STATUS_BADGE[v.status] ?? 'badge-gray'}`}>{v.status}</span>
                                </div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--muted)' }}>
                                    ⚡ {v.speed ?? 0} knots · 📍 {v.latitude?.toFixed(4)}, {v.longitude?.toFixed(4)}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Map */}
                <div style={{ borderRadius: 'var(--r-lg)', overflow: 'hidden', border: '1px solid var(--border)', position: 'relative' }}>
                    {typeof window !== 'undefined' && (
                        <MapContainer
                            center={center}
                            zoom={5}
                            style={{ height: '100%', width: '100%', background: '#0b1527' }}
                            ref={mapRef}
                        >
                            <TileLayer
                                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                                attribution='&copy; CartoDB'
                            />
                            {vessels.map(v => (
                                <Marker key={v.code_vessel} position={[v.latitude || 0, v.longitude || 0]}>
                                    <Popup>
                                        <div style={{ fontFamily: 'var(--font)', minWidth: 160 }}>
                                            <strong>{v.name || v.code_vessel}</strong><br />
                                            Status: {v.status}<br />
                                            Kecepatan: {v.speed ?? 0} knots<br />
                                            Update: {v.last_update ? new Date(v.last_update).toLocaleString('id-ID') : '—'}
                                        </div>
                                    </Popup>
                                </Marker>
                            ))}
                        </MapContainer>
                    )}

                    {vessels.length === 0 && !loading && (
                        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center', color: 'var(--muted)', zIndex: 1000 }}>
                            <div style={{ fontSize: '2rem', marginBottom: 8 }}>🚢</div>
                            <div>Belum ada data posisi kapal tercatat</div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
