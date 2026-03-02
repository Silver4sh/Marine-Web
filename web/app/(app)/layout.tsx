import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import AppShell from '@/components/layout/AppShell';

export default async function AuthLayout({ children }: { children: React.ReactNode }) {
    const session = await getSession();
    if (!session.loggedIn) redirect('/login');

    return (
        <AppShell session={{ username: session.username, role: session.role, name: session.name }}>
            {children}
        </AppShell>
    );
}
