import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query(`
      SELECT DISTINCT ON (vp.id_vessel)
        vp.id_vessel as code_vessel,
        v.name,
        v.flag,
        v.status,
        vp.latitude,
        vp.longitude,
        vp.speed,
        vp.heading,
        vp.created_at as last_update
      FROM operation.vessel_positions vp
      JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
      ORDER BY vp.id_vessel, vp.created_at DESC
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[vessels/positions/GET]', err);
        return NextResponse.json([]);
    }
}
