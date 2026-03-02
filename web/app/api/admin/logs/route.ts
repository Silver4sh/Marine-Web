import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn || session.role !== 'Admin') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    try {
        const rows = await query(`
      SELECT changed_by, table_name, action, old_data, new_data, changed_at
      FROM audit.audit_logs
      WHERE changed_at >= NOW() - INTERVAL '7 days'
      ORDER BY changed_at DESC
      LIMIT 200
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[admin/logs/GET]', err);
        return NextResponse.json([]);
    }
}
