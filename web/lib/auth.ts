import { getIronSession, IronSession } from 'iron-session';
import { cookies } from 'next/headers';

export interface SessionData {
    username: string;
    role: string;
    name: string;
    loggedIn: boolean;
}

const sessionOptions = {
    password: process.env.SESSION_SECRET || 'marine-os-super-secret-key-minimum32ch',
    cookieName: 'marineos-session',
    cookieOptions: {
        secure: process.env.NODE_ENV === 'production',
        httpOnly: true,
        maxAge: 60 * 60 * 8, // 8 hours
    },
};

export async function getSession(): Promise<IronSession<SessionData>> {
    const cookieStore = await cookies();
    return getIronSession<SessionData>(cookieStore, sessionOptions);
}
