// app/diet/page.tsx
'use client';
import React, { useState } from 'react';
import useFailoverFetch from '../../utils/fetchFailover';


function DietCard({ day, meals }: any) {
return (
<div className="rounded-xl border border-slate-300 bg-white shadow-sm p-4">
<h3 className="font-semibold text-slate-900 mb-2">{day}</h3>
<ul className="space-y-1 text-sm text-slate-700">
<li><span className="font-medium">Breakfast:</span> {meals.breakfast}</li>
<li><span className="font-medium">Lunch:</span> {meals.lunch}</li>
<li><span className="font-medium">Dinner:</span> {meals.dinner}</li>
</ul>
</div>
);
}


export default function DietPage() {
const { data: pantry } = useFailoverFetch('/api/pantry', { fallbackPath: '/data/pantry.mock.json' });
const [mode, setMode] = useState<'week'|'month'>('week');
const [plan, setPlan] = useState<any | null>(null);
const [loading, setLoading] = useState(false);


async function generate() {
setLoading(true);
const res = await fetch(`/api/diet/${mode}`, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ pantry })
});
const json = await res.json();
setPlan(json.plan);
setLoading(false);
}


return (
<div className="space-y-6">
<h1 className="text-3xl font-bold text-slate-900">Diet Generator</h1>
<p className="text-slate-600 max-w-2xl">Diet plans are generated strictly from pantry items. If the pantry is insufficient, foods are randomly filled from the database.</p>


<div className="flex flex-wrap gap-2">
<button onClick={() => setMode('week')} className={`px-4 py-2 rounded-lg font-medium ${mode==='week' ? 'bg-blue-600 text-white' : 'bg-slate-300 text-slate-800'}`}>Weekly</button>
<button onClick={() => setMode('month')} className={`px-4 py-2 rounded-lg font-medium ${mode==='month' ? 'bg-blue-600 text-white' : 'bg-slate-300 text-slate-800'}`}>Monthly</button>
<button onClick={generate} className="px-4 py-2 rounded-lg bg-green-600 text-white font-medium">Generate Diet</button>
</div>


{loading && <div className="text-slate-600">Generating diet plan…</div>}


{plan && (
<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
{Object.entries(plan).map(([day, meals]: any) => (
<DietCard key={day} day={day} meals={meals} />
))}
</div>
)}
</div>
);
}