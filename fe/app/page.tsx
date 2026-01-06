// app/page.tsx
import Link from 'next/link';


export default function HomePage() {
return (
<div className="space-y-6">
<h1 className="text-3xl font-bold">Welcome to NutritionApp</h1>
<p className="text-slate-600">Quick links to manage your pantry and generate diet plans.</p>


<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
<Link href="/pantry" className="p-6 bg-white rounded shadow hover:shadow-md">
<h2 className="text-xl font-semibold">Pantry</h2>
<p className="mt-2 text-slate-500">View and add items to your pantry.</p>
</Link>


<Link href="/diet" className="p-6 bg-white rounded shadow hover:shadow-md">
<h2 className="text-xl font-semibold">Diet Generator</h2>
<p className="mt-2 text-slate-500">Generate weekly or monthly diet plans from your pantry.</p>
</Link>
</div>
</div>
);
}