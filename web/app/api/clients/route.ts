import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query(`
      SELECT c.code_client, c.name, c.industry, c.region, c.status,
             COUNT(DISTINCT o.id) as total_orders,
             COALESCE(SUM(p.total_amount), 0) as ltv
      FROM operation.clients c
      LEFT JOIN operation.orders o ON c.code_client = o.id_client
      LEFT JOIN operation.payments p ON o.code_order = p.id_order AND p.status = 'Completed'
      WHERE c.deleted_at IS NULL
      GROUP BY c.code_client, c.name, c.industry, c.region, c.status
      ORDER BY ltv DESC
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[clients/GET]', err);
        return NextResponse.json([]);
    }
}
