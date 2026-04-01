'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

export default function PitchersPage() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { fetchApi('/api/pitchers?site=dk').then(setRows).catch(()=>setRows([])); }, []);
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Pitchers</h1><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Name</th><th>Salary</th><th>Proj</th><th>Ceiling</th><th>Cash</th><th>GPP</th></tr></thead><tbody>{rows.map((p:any)=><tr key={p.player_id} className="border-t border-slate-800"><td><Link href={`/player/${p.player_id}`}>{p.name}</Link></td><td>{p.salary}</td><td>{Number(p.projection||0).toFixed(2)}</td><td>{Number(p.ceiling||0).toFixed(2)}</td><td>{Number(p.cash_safety||0).toFixed(2)}</td><td>{Number(p.gpp_upside||0).toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
