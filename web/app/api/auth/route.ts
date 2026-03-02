import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getSession } from '@/lib/auth';

export async function POST(req: NextRequest) {
    try {
        const { username, password } = await req.json();
        if (!username || !password) {
            return NextResponse.json({ error: 'Username dan password wajib diisi' }, { status: 400 });
        }

        const rows = await query<{ code_user: string; role: string; name: string; status: string }>(
            `SELECT u.code_user, u.role, u.name, u.status
       FROM operation.users u
       JOIN operation.user_managements um ON u.code_user = um.id_user
       WHERE um.id_user = $1 AND um.password = $2 AND um.status = 'Active' AND u.status = 'Active'`,
            [username, password]
        );

        if (rows.length === 0) {
            return NextResponse.json({ error: 'Username atau password salah' }, { status: 401 });
        }

        const user = rows[0];
        await query(
            `UPDATE operation.user_managements SET last_login = NOW() WHERE id_user = $1`,
            [username]
        );

        const session = await getSession();
        session.username = user.code_user;
        session.role = user.role;
        session.name = user.name;
        session.loggedIn = true;
        await session.save();

        return NextResponse.json({ username: user.code_user, role: user.role, name: user.name });
    } catch (err) {
        console.error('[auth/POST]', err);
        return NextResponse.json({ error: 'Server error' }, { status: 500 });
    }
}

export async function DELETE() {
    const session = await getSession();
    session.destroy();
    return NextResponse.json({ ok: true });
}

export async function GET() {
    const session = await getSession();
    if (!session.loggedIn) {
        return NextResponse.json({ loggedIn: false }, { status: 401 });
    }
    return NextResponse.json({
        loggedIn: true,
        username: session.username,
        role: session.role,
        name: session.name,
    });
}
