'use client';
import { useEffect, useMemo, useState } from 'react';

export default function LineupBuilder() {
  const [rows, setRows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any[]>([]);
  useEffect(() => { fetch('http://localhost:8000/api/hitters?site=dk').then(r=>r.json()).then(setRows); }, []);
  const salary = useMemo(() => selected.reduce((a, b) => a + (b.salary || 0), 0), [selected]);

  return <div className="space-y-4"><h1 className="text-2xl font-bold">Lineup Builder Sandbox</h1><p>Selected Salary: {salary} | Remaining (50K DK): {50000 - salary}</p><div className="grid grid-cols-2 gap-4"><div className="card max-h-[600px] overflow-auto">{rows.slice(0,120).map((r)=> <div key={r.player_id} className="flex justify-between border-b border-slate-800 py-1"><span>{r.name} ({r.team})</span><button className="text-sky-300" onClick={()=>setSelected((s)=>[...s,r])}>Add</button></div>)}</div><div className="card">{selected.map((s,idx)=><div key={`${s.player_id}-${idx}`} className="flex justify-between border-b border-slate-800 py-1"><span>{s.name}</span><span>{s.salary}</span></div>)}</div></div></div>
}
