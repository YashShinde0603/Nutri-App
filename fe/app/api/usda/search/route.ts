// app/api/usda/search/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';


export async function GET(req: Request) {
// Read query param q
const url = new URL(req.url);
const q = url.searchParams.get('q') || '';


// Simulate backend instability 25% chance
if (Math.random() < 0.25) return new NextResponse('Backend timeout', { status: 504 });


// Serve a subset of foods.json
const file = path.join(process.cwd(), 'public', 'data', 'foods.json');
const raw = fs.readFileSync(file, 'utf-8');
const foods = JSON.parse(raw) as any[];
const filtered = foods.filter(f => f.description.toLowerCase().includes(q.toLowerCase())).slice(0, 100);
return NextResponse.json(filtered);
}