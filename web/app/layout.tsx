import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MarineOS — Marine Operations Dashboard',
  description: 'Real-time marine operations, fleet monitoring, and analytics platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
