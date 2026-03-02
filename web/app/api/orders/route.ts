import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query(`
      SELECT
        COUNT(*) as total_orders,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END) as in_completed,
        SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END) as on_progress,
        SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open,
        SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed
      FROM operation.orders
    `);
        const d = rows[0] || {};
        return NextResponse.json({
            total_orders: Number(d.total_orders) || 0,
            completed: Number(d.completed) || 0,
            in_completed: Number(d.in_completed) || 0,
            on_progress: Number(d.on_progress) || 0,
            open: Number(d.open) || 0,
            failed: Number(d.failed) || 0,
        });
    } catch (err) {
        console.error('[orders/GET]', err);
        return NextResponse.json({ total_orders: 0, completed: 0, in_completed: 0, on_progress: 0, open: 0, failed: 0 });
    }
}
