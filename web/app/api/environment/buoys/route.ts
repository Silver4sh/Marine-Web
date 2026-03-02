import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query(`
      SELECT
        b.code_buoy,
        b.status,
        b.latitude,
        b.longitude,
        s.location,
        MAX(bsh.created_at) as last_update
      FROM ocean.buoys b
      LEFT JOIN ocean.buoy_sensor_histories bsh ON b.code_buoy = bsh.id_buoy
      LEFT JOIN operation.sites s ON b.id_site = s.code_site
      WHERE b.deleted_at IS NULL
      GROUP BY b.code_buoy, b.status, b.latitude, b.longitude, s.location
      ORDER BY b.code_buoy
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[buoys/GET]', err);
        return NextResponse.json([]);
    }
}
