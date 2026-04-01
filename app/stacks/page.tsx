'use client';
import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

export default function StacksPage() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { fetchApi('/api/stacks?site=dk').then(setRows).catch(()=>setRows([])); }, []);
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Stacks</h1><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Team</th><th>Stack</th><th>Ceiling</th><th>Value</th><th>Own%</th><th>Lev</th></tr></thead><tbody>{rows.map((s:any)=><tr key={s.team} className="border-t border-slate-800"><td>{s.team}</td><td>{Number(s.stack_score||0).toFixed(2)}</td><td>{Number(s.ceiling_score||0).toFixed(2)}</td><td>{Number(s.value_score||0).toFixed(2)}</td><td>{s.ownership_proxy}</td><td>{Number(s.leverage_score||0).toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
