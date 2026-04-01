'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function ValueBarChart({ data, xKey='name', yKey='value_score' }: { data: any[]; xKey?: string; yKey?: string }) {
  return <div className="h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={data}><XAxis dataKey={xKey} hide /><YAxis /><Tooltip /><Bar dataKey={yKey} fill="#38bdf8"/></BarChart></ResponsiveContainer></div>;
}
