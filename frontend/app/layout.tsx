import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import '@livekit/components-styles';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Odoo Technical Support Agent',
  description: 'AI-powered voice support agent for Odoo',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
