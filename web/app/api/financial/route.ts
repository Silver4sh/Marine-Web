import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        // Current month revenue
        const [curr] = await query<{ total_revenue: string; completed_orders: string }>(`
      SELECT COALESCE(SUM(total_amount), 0) as total_revenue,
             COUNT(DISTINCT id_order) as completed_orders
      FROM operation.payments WHERE status = 'Completed'
        AND DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', NOW())
    `);
        // Last month revenue
        const [prev] = await query<{ total_revenue: string }>(`
      SELECT COALESCE(SUM(total_amount), 0) as total_revenue
      FROM operation.payments WHERE status = 'Completed'
        AND DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', NOW() - INTERVAL '1 month')
    `);

        const current = parseFloat(curr?.total_revenue || '0');
        const previous = parseFloat(prev?.total_revenue || '0');
        const delta = previous > 0 ? ((current - previous) / previous) * 100 : 0;

        // Monthly revenue for chart
        const monthly = await query<{ month: string; revenue: string }>(`
      SELECT TO_CHAR(DATE_TRUNC('month', payment_date), 'Mon YY') as month,
             SUM(total_amount) as revenue
      FROM operation.payments WHERE status = 'Completed'
      GROUP BY DATE_TRUNC('month', payment_date)
      ORDER BY DATE_TRUNC('month', payment_date) ASC
      LIMIT 12
    `);

        return NextResponse.json({
            total_revenue: current,
            completed_orders: Number(curr?.completed_orders) || 0,
            delta_revenue: Math.round(delta * 10) / 10,
            monthly_revenue: monthly.map(r => ({ month: r.month, revenue: parseFloat(r.revenue) })),
        });
    } catch (err) {
        console.error('[financial/GET]', err);
        return NextResponse.json({ total_revenue: 0, completed_orders: 0, delta_revenue: 0, monthly_revenue: [] });
    }
}
