import { fetchApi } from '../../lib/api';

export default async function GamesPage() {
  const data = await fetchApi('/api/games');
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Games Context</h1><div className="grid grid-cols-1 md:grid-cols-3 gap-3">{data.team_context.map((t:any)=><div key={t.team} className="card"><h3 className="font-semibold">{t.team}</h3><p>wOBA: {t.woba}</p><p>ISO: {t.iso}</p><p>Bullpen weakness: {t.bullpen_weakness}</p></div>)}</div></div>
}
