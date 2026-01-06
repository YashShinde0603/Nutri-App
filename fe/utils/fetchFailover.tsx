// utils/fetchFailover.tsx
'use client';
import { useEffect, useState } from 'react';


export default function useFailoverFetch<T = any>(url: string, opts: { timeoutMs?: number, fallbackPath?: string } = {}) {
const { timeoutMs = 5000, fallbackPath } = opts;
const [data, setData] = useState<T | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<any>(null);


useEffect(() => {
let mounted = true;


async function fetchData() {
setLoading(true);
setError(null);
try {
const controller = new AbortController();
const id = setTimeout(() => controller.abort(), timeoutMs);


const res = await fetch(url, { signal: controller.signal });
clearTimeout(id);


if (!res.ok) throw new Error(`Status ${res.status}`);


const json = await res.json();
if (!mounted) return;
setData(json);
setLoading(false);
} catch (err) {
// On any error, try fallbackPath (local JSON) if provided
setError(err);
if (fallbackPath) {
try {
const fallbackRes = await fetch(fallbackPath);
const fallbackJson = await fallbackRes.json();
if (!mounted) return;
setData(fallbackJson);
} catch (fallbackErr) {
if (!mounted) return;
setError({ primary: err, fallback: fallbackErr });
}
}
setLoading(false);
}
}


fetchData();


return () => { mounted = false; };
}, [url, timeoutMs, fallbackPath]);


return { data, loading, error } as const;
}