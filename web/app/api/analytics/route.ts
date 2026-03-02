import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        // Monthly revenue
        const monthly = await query<{ month: string; revenue: string }>(`
      SELECT TO_CHAR(DATE_TRUNC('month', payment_date), 'Mon YY') as month,
             SUM(total_amount) as revenue
      FROM operation.payments WHERE status = 'Completed'
      GROUP BY DATE_TRUNC('month', payment_date)
      ORDER BY DATE_TRUNC('month', payment_date) ASC
      LIMIT 12
    `);

        // Correlation data - revenue cycle
        const cycle = await query(`
      SELECT DATE_TRUNC('month', o.order_date) as month,
             AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) as avg_days_to_cash,
             SUM(p.total_amount) as realized_revenue,
             SUM(CASE WHEN p.status = 'Completed' THEN 1 ELSE 0 END) as paid_count,
             COUNT(o.code_order) as total_orders
      FROM operation.orders o
      JOIN operation.payments p ON o.code_order = p.id_order
      WHERE o.order_date >= NOW() - INTERVAL '6 months'
      GROUP BY 1 ORDER BY 1 DESC
    `);

        // Logistics performance
        const logistics = await query(`
      SELECT destination,
             COUNT(*) as total_trips,
             AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date))/3600) as avg_delay_hours
      FROM operation.orders
      WHERE actual_delivery_date IS NOT NULL AND scheduled_delivery_date IS NOT NULL
      GROUP BY destination ORDER BY avg_delay_hours DESC
      LIMIT 10
    `);

        const revenueData = monthly.map(r => ({ month: r.month, revenue: parseFloat(r.revenue) }));

        // Simple linear forecast: 6 months ahead
        const forecast = [];
        if (revenueData.length >= 3) {
            const n = revenueData.length;
            const x = revenueData.map((_, i) => i);
            const y = revenueData.map(d => d.revenue);
            const sumX = x.reduce((a, b) => a + b, 0);
            const sumY = y.reduce((a, b) => a + b, 0);
            const sumXY = x.reduce((a, i) => a + i * y[i], 0);
            const sumX2 = x.reduce((a, b) => a + b * b, 0);
            const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            const intercept = (sumY - slope * sumX) / n;

            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const now = new Date();
            for (let i = 1; i <= 6; i++) {
                const predicted = Math.max(0, intercept + slope * (n + i - 1));
                const futureMonth = new Date(now.getFullYear(), now.getMonth() + i, 1);
                forecast.push({
                    month: `${months[futureMonth.getMonth()]} ${String(futureMonth.getFullYear()).slice(-2)}`,
                    revenue: Math.round(predicted),
                    isForecast: true,
                });
            }
        }

        return NextResponse.json({
            monthly_revenue: revenueData,
            forecast,
            cycle,
            logistics,
        });
    } catch (err) {
        console.error('[analytics/GET]', err);
        return NextResponse.json({ monthly_revenue: [], forecast: [], cycle: [], logistics: [] });
    }
}
