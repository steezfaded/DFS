'use client';
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function ProjectionSalaryScatter({ data }: { data: any[] }) {
  return <div className="h-72"><ResponsiveContainer width="100%" height="100%"><ScatterChart><XAxis dataKey="salary" name="Salary"/><YAxis dataKey="projection" name="Projection"/><Tooltip cursor={{ strokeDasharray: '3 3' }} /><Scatter data={data} fill="#22c55e"/></ScatterChart></ResponsiveContainer></div>;
}
