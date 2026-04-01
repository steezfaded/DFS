'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';
import { ProjectionSalaryScatter } from '../../components/ProjectionSalaryScatter';

export default function HittersPage() {
  const [hitters, setHitters] = useState<any[]>([]);
  useEffect(() => { fetchApi('/api/hitters?site=dk').then(setHitters).catch(()=>setHitters([])); }, []);
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Hitters</h1><div className="card"><ProjectionSalaryScatter data={hitters.filter((h:any)=>h.salary)} /></div><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Name</th><th>Team</th><th>Salary</th><th>Proj</th><th>Value</th><th>Lev</th></tr></thead><tbody>{hitters.slice(0,250).map((h:any)=><tr key={h.player_id} className="border-t border-slate-800"><td><Link href={`/player/${h.player_id}`}>{h.name}</Link></td><td>{h.team}</td><td>{h.salary}</td><td>{Number(h.projection||0).toFixed(2)}</td><td>{Number(h.value_score||0).toFixed(2)}</td><td>{Number(h.leverage_score||0).toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
