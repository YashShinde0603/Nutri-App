import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Nutri-App",
  description: "Nutrition planning made simple",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Top Navigation */}
        <header className="border-b bg-white">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <Link href="/" className="text-xl font-semibold text-brand">
              Nutri-App
            </Link>

            <nav className="flex gap-6 text-sm font-medium">
              <Link href="/" className="hover:text-brand">
                Home
              </Link>
              <Link href="/pantry" className="hover:text-brand">
                Pantry
              </Link>
              <Link href="/diet" className="hover:text-brand">
                Diet
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="mx-auto max-w-6xl px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
