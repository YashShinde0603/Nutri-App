// app/pantry/add/page.tsx
'use client';
import React, { useEffect, useState } from 'react';
import useFailoverFetch from '../../../utils/fetchFailover';


export default function AddItemPage() {
const { data: foods, loading, error } = useFailoverFetch('/api/usda/search?q=', {
fallbackPath: '/data/foods.json',
});


const [query, setQuery] = useState('');
const [filtered, setFiltered] = useState<any[]>([]);
const [selected, setSelected] = useState<any | null>(null);
const [saved, setSaved] = useState(false);


useEffect(() => {
if (!foods) return;
const q = query.toLowerCase();
const list = (foods as any[]).filter((f: any) => f.description.toLowerCase().includes(q));
setFiltered(list.slice(0, 50));
}, [query, foods]);


function addToPantry() {
// mock add: POST to /api/pantry
fetch('/api/pantry', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ name: selected?.description || query, quantity: 1, category: 'Uncategorized' }),
}).then(() => setSaved(true));
}


return (
<div className="space-y-4">
<h1 className="text-2xl font-bold">Add Item</h1>
<div className="space-y-2">
<input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search foods..." className="w-full p-2 border rounded" />
{loading && <div>Loading foods...</div>}
{error && <div className="text-red-600">Backend unavailable — using local foods.json.</div>}


<div className="max-h-72 overflow-auto bg-white rounded shadow p-2">
{filtered.map((f: any) => (
<div key={f.fdcId} className={`p-2 rounded hover:bg-slate-50 cursor-pointer flex justify-between ${selected?.fdcId === f.fdcId ? 'bg-slate-100' : ''}`} onClick={() => setSelected(f)}>
<div>
<div className="font-medium">{f.description}</div>
<div className="text-sm text-slate-500">{(f.foodNutrients || []).slice(0,3).map((n:any)=> `${n.nutrientName}: ${n.value}${n.unitName}`).join(' • ')}</div>
</div>
<div className="text-sm text-slate-400">ID: {f.fdcId}</div>
</div>
))}
</div>


<div className="flex gap-2">
<button onClick={addToPantry} className="px-4 py-2 bg-green-600 text-white rounded" disabled={!selected && !query}>Add</button>
{saved && <div className="text-green-700">Saved to pantry (mock)</div>}
</div>
</div>
</div>
);
}