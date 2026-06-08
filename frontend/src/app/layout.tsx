import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Developer DNA",
  description: "AI-powered developer telemetry",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-50 min-h-screen selection:bg-blue-500/30 selection:text-blue-200`}>
        <Sidebar />
        <div className="pl-64 min-h-screen flex flex-col relative">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-violet-500/5 to-transparent pointer-events-none" />
          <Header />
          <main className="flex-1 p-8 relative z-0">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
