// app/layout.tsx
import './globals.css';
import React from 'react';
import Link from 'next/link';


export const metadata = {
title: 'Nutrition App',
description: 'Pantry + Diet Generator',
};


export default function RootLayout({ children }: { children: React.ReactNode }) {
return (
<html lang="en">
<body className="min-h-screen bg-slate-50 text-slate-800">
<header className="bg-white shadow-sm sticky top-0 z-10">
<div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
<Link href="/" className="text-xl font-bold">NutritionApp</Link>
<nav className="flex gap-3">
<Link href="/pantry" className="px-3 py-1 rounded hover:bg-slate-100">Pantry</Link>
<Link href="/diet" className="px-3 py-1 rounded hover:bg-slate-100">Diet Generator</Link>
</nav>
</div>
</header>
<main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
<footer className="text-center text-sm text-slate-500 py-6">Built with ❤️ • Example app</footer>
</body>
</html>
);
}