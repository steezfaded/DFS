import { fetchApi } from '../../../lib/api';

export default async function PlayerPage({ params }: { params: { id: string } }) {
  const p = await fetchApi(`/api/player/${params.id}`);
  return <div className="space-y-3"><h1 className="text-2xl font-bold">{p.name}</h1><div className="card"><p>Positions: {p.positions || 'N/A'}</p><p>Type: {p.is_pitcher ? 'Pitcher' : 'Hitter'}</p><p>Data quality note: public feeds may lag same-day lineup and status changes.</p></div></div>
}
