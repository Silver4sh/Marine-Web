import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET(
    _req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { id } = await params;
    try {
        const rows = await query(`
      SELECT id_buoy, created_at, salinitas, turbidity, oxygen, density, current, tide
      FROM ocean.buoy_sensor_histories
      WHERE id_buoy = $1
      ORDER BY created_at ASC
      LIMIT 500
    `, [id]);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[buoy-sensor/GET]', err);
        return NextResponse.json([]);
    }
}
