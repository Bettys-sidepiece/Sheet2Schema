import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import clsx from "clsx";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sheet2Schema",
  description: "Convert spreadsheets into database schemas and ORM models",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={clsx(poppins.variable)}>
      <body className="min-h-screen font-sans bg-gray-50">
        <header>
          <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-center">
            <h1 className="text-6xl font-semibold text-black">
              Sheet2Schema
            </h1>
          </div>
        </header>

        <main className="flex flex-col items-center justify-center flex-1 mx-auto w-full max-w-6xl px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
