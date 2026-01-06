// app/pantry/page.tsx
'use client';
import React from 'react';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import useFailoverFetch from '../../utils/fetchFailover';


export default function PantryPage() {
const { data, loading, error } = useFailoverFetch('/api/pantry', {
fallbackPath: '/data/pantry.mock.json',
});


return (
<div className="space-y-4">
<div className="flex items-center justify-between">
<h1 className="text-2xl font-bold">Your Pantry</h1>
<Link href="/pantry/add" className="px-3 py-1 bg-blue-600 text-white rounded">Add Item</Link>
</div>


{loading && <div>Loading pantry...</div>}
{error && <div className="text-red-600">Couldn't load from backend — using local data.</div>}


<div className="grid gap-3">
{Array.isArray(data) && data.length ? (
data.map((item: any) => (
<div key={item.id} className="p-3 bg-white rounded shadow-sm flex justify-between">
<div>
<div className="font-semibold">{item.name}</div>
<div className="text-sm text-slate-500">Qty: {item.quantity} • Category: {item.category}</div>
</div>
<div className="text-sm text-slate-500">Added: {new Date(item.addedAt).toLocaleDateString()}</div>
</div>
))
) : (
<div className="p-4 bg-white rounded">No items found in your pantry.</div>
)}
</div>
</div>
);
}