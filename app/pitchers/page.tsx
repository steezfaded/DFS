import Link from 'next/link';
import { fetchApi } from '../../lib/api';

export default async function PitchersPage() {
  const rows = await fetchApi('/api/pitchers?site=dk');
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Pitchers</h1><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Name</th><th>Salary</th><th>Proj</th><th>Ceiling</th><th>Cash</th><th>GPP</th></tr></thead><tbody>{rows.map((p:any)=><tr key={p.player_id} className="border-t border-slate-800"><td><Link href={`/player/${p.player_id}`}>{p.name}</Link></td><td>{p.salary}</td><td>{p.projection.toFixed(2)}</td><td>{p.ceiling.toFixed(2)}</td><td>{p.cash_safety.toFixed(2)}</td><td>{p.gpp_upside.toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
