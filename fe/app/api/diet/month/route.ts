// app/api/diet/month/route.ts
import { NextResponse } from 'next/server';


function samplePlanFromPantry(pantry: any[]) {
const days = 30;
const plan: any = {};
for (let d = 0; d < days; d++) {
plan[`Day ${d+1}`] = {
breakfast: pantry[d % pantry.length]?.name || 'Cereal',
lunch: pantry[(d+1) % pantry.length]?.name || 'Salad',
dinner: pantry[(d+2) % pantry.length]?.name || 'Rice & Veg',
};
}
return plan;
}


export async function POST(request: Request) {
try {
const { pantry } = await request.json();
const plan = samplePlanFromPantry(Array.isArray(pantry) && pantry.length ? pantry : []);
return NextResponse.json({ mode: 'monthly', plan });
} catch (e) {
return new NextResponse('Invalid', { status: 400 });
}
}