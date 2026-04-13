import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import 'mapbox-gl/dist/mapbox-gl.css';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Geo-LLM Spatial RAG Engine",
  description: "Natural Language to PostGIS translated map interface.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-neutral-900 text-slate-100 antialiased overflow-hidden`}>
        {children}
      </body>
    </html>
  );
}
