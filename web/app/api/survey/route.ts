import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const rows = await query(`
      SELECT
        sl.id,
        sl.doc_no as code_report,
        sl.log_date as date_survey,
        si.location as site_name,
        v.name as vessel_name,
        u.name as surveyor_name,
        sl.sample_type,
        sl.total_sample,
        sl.packages_number
      FROM log.sample_logs sl
      LEFT JOIN operation.sites si ON sl.id_site = si.code_site
      LEFT JOIN operation.vessels v ON sl.id_vessel = v.code_vessel
      LEFT JOIN operation.users u ON sl.id_surveyor = u.code_user
      WHERE sl.deleted_at IS NULL
      ORDER BY sl.log_date DESC
      LIMIT 100
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[survey/GET]', err);
        return NextResponse.json([]);
    }
}

export async function POST(req: NextRequest) {
    const session = await getSession();
    if (!session.loggedIn) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    try {
        const data = await req.json();

        // Auto-generate doc_no
        const timestamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
        const docNo = `SRV-${timestamp}`;

        await query(`
      INSERT INTO log.sample_logs (id_vessel, id_surveyor, id_captain, id_site, doc_no, log_date, sample_type, total_sample, packages_number)
      VALUES ($1, $2, $2, $3, $4, $5, $6, $7, $8)
    `, [
            data.id_vessel,
            session.username,
            data.id_site,
            docNo,
            data.date_survey || new Date().toISOString(),
            data.sample_type || 'Field Survey',
            data.total_sample || 0,
            data.packages_number || 0,
        ]);

        return NextResponse.json({ ok: true, doc_no: docNo });
    } catch (err) {
        console.error('[survey/POST]', err);
        return NextResponse.json({ error: String(err) }, { status: 500 });
    }
}
