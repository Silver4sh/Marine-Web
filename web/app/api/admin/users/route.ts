import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn || session.role !== 'Admin') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    try {
        const rows = await query(`
      SELECT u.code_user, um.id_user as username, u.name, u.role, u.status as user_status,
             um.status as account_status, um.last_login
      FROM operation.users u
      JOIN operation.user_managements um ON u.code_user = um.id_user
      ORDER BY u.code_user ASC
    `);
        return NextResponse.json(rows);
    } catch (err) {
        console.error('[admin/users/GET]', err);
        return NextResponse.json([]);
    }
}

export async function POST(req: NextRequest) {
    const session = await getSession();
    if (!session.loggedIn || session.role !== 'Admin') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    try {
        const { username, password, role, name } = await req.json();
        const existing = await query(`SELECT 1 FROM operation.users WHERE code_user = $1`, [username]);
        if (existing.length > 0) {
            return NextResponse.json({ error: 'Pengguna sudah ada' }, { status: 409 });
        }
        // Generate contact code
        const codeContact = `CTK-${username.toUpperCase()}`;
        await query(`
      INSERT INTO operation.contacts (code_contact, email) VALUES ($1, $2)
      ON CONFLICT DO NOTHING
    `, [codeContact, `${username}@marineos.local`]);
        await query(`
      INSERT INTO operation.users (id_contact, code_user, name, citizen, role, status, organs)
      VALUES ($1, $2, $3, 'Indonesia', $4, 'Active', 'Internal')
    `, [codeContact, username, name || username, role]);
        await query(`
      INSERT INTO operation.user_managements (id_user, password, status)
      VALUES ($1, $2, 'Active')
    `, [username, password]);
        return NextResponse.json({ ok: true });
    } catch (err) {
        console.error('[admin/users/POST]', err);
        return NextResponse.json({ error: String(err) }, { status: 500 });
    }
}

export async function PATCH(req: NextRequest) {
    const session = await getSession();
    if (!session.loggedIn || session.role !== 'Admin') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    try {
        const { username, role, status } = await req.json();
        if (role) await query(`UPDATE operation.users SET role = $1 WHERE code_user = $2`, [role, username]);
        if (status) {
            await query(`UPDATE operation.users SET status = $1 WHERE code_user = $2`, [status, username]);
            await query(`UPDATE operation.user_managements SET status = $1 WHERE id_user = $2`, [status, username]);
        }
        return NextResponse.json({ ok: true });
    } catch (err) {
        console.error('[admin/users/PATCH]', err);
        return NextResponse.json({ error: String(err) }, { status: 500 });
    }
}

export async function DELETE(req: NextRequest) {
    const session = await getSession();
    if (!session.loggedIn || session.role !== 'Admin') {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    try {
        const { username } = await req.json();
        if (username === session.username) {
            return NextResponse.json({ error: 'Tidak dapat menghapus akun sendiri' }, { status: 400 });
        }
        await query(`DELETE FROM operation.user_managements WHERE id_user = $1`, [username]);
        await query(`DELETE FROM operation.users WHERE code_user = $1`, [username]);
        return NextResponse.json({ ok: true });
    } catch (err) {
        console.error('[admin/users/DELETE]', err);
        return NextResponse.json({ error: String(err) }, { status: 500 });
    }
}
