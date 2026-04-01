import { fetchApi } from '../../lib/api';

export default async function StacksPage() {
  const rows = await fetchApi('/api/stacks?site=dk');
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Stacks</h1><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Team</th><th>Stack</th><th>Ceiling</th><th>Value</th><th>Own%</th><th>Lev</th></tr></thead><tbody>{rows.map((s:any)=><tr key={s.team} className="border-t border-slate-800"><td>{s.team}</td><td>{s.stack_score.toFixed(2)}</td><td>{s.ceiling_score.toFixed(2)}</td><td>{s.value_score.toFixed(2)}</td><td>{s.ownership_proxy}</td><td>{s.leverage_score.toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
