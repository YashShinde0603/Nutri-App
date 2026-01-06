// app/api/pantry/route.ts
import { NextResponse } from 'next/server';


let inMemoryPantry = [
{ id: 'p1', name: 'Apple', quantity: 6, category: 'Fruits', addedAt: new Date().toISOString() },
{ id: 'p2', name: 'Brown Rice (uncooked)', quantity: 2, category: 'Grains', addedAt: new Date().toISOString() },
];


export async function GET() {
// Simulate occasional backend failure (for demo failover): 20% chance
if (Math.random() < 0.2) return new NextResponse('Backend error', { status: 500 });
return NextResponse.json(inMemoryPantry);
}


export async function POST(request: Request) {
try {
const body = await request.json();
const newItem = { id: `p${Date.now()}`, ...body, addedAt: new Date().toISOString() };
inMemoryPantry.unshift(newItem);
return NextResponse.json(newItem);
} catch (e) {
return new NextResponse('Invalid', { status: 400 });
}
}