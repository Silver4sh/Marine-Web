import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query<Record<string, number>>(`
      SELECT
        COUNT(*) as total_vessels,
        SUM(CASE WHEN LOWER(va.status) IN ('operating','dredging','delivering') THEN 1 ELSE 0 END) as operating,
        SUM(CASE WHEN LOWER(va.status) IN ('maintenance','docking','mtc') THEN 1 ELSE 0 END) as maintenance,
        SUM(CASE WHEN LOWER(va.status) = 'idle' OR va.status IS NULL THEN 1 ELSE 0 END) as idle
      FROM operation.vessels v
      LEFT JOIN operation.vessel_activities va ON v.code_vessel = va.id_vessel
        AND va.seq_activity = (
          SELECT MAX(vva.seq_activity)
          FROM operation.vessel_activities vva
          WHERE vva.id_vessel = v.code_vessel
        )
    `);

        const data = rows[0] || { total_vessels: 0, operating: 0, maintenance: 0, idle: 0 };
        return NextResponse.json({
            total_vessels: Number(data.total_vessels) || 0,
            operating: Number(data.operating) || 0,
            maintenance: Number(data.maintenance) || 0,
            idle: Number(data.idle) || 0,
        });
    } catch (err) {
        console.error('[fleet/GET]', err);
        return NextResponse.json({ total_vessels: 0, operating: 0, maintenance: 0, idle: 0 });
    }
}
