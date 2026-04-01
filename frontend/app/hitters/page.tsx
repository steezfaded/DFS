import Link from 'next/link';
import { fetchApi } from '../../lib/api';
import { ProjectionSalaryScatter } from '../../components/ProjectionSalaryScatter';

export default async function HittersPage() {
  const hitters = await fetchApi('/api/hitters?site=dk');
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Hitters</h1><div className="card"><ProjectionSalaryScatter data={hitters.filter((h:any)=>h.salary)} /></div><div className="card overflow-auto"><table className="w-full text-sm"><thead><tr><th>Name</th><th>Team</th><th>Salary</th><th>Proj</th><th>Value</th><th>Lev</th></tr></thead><tbody>{hitters.slice(0,250).map((h:any)=><tr key={h.player_id} className="border-t border-slate-800"><td><Link href={`/player/${h.player_id}`}>{h.name}</Link></td><td>{h.team}</td><td>{h.salary}</td><td>{h.projection.toFixed(2)}</td><td>{h.value_score.toFixed(2)}</td><td>{h.leverage_score.toFixed(2)}</td></tr>)}</tbody></table></div></div>
}
