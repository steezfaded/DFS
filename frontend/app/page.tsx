import { fetchApi } from '../lib/api';
import { ValueBarChart } from '../components/ValueBarChart';

export default async function Page() {
  const data = await fetchApi('/api/overview?site=dk');
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">MLB DFS Command Center</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card"><h2 className="font-semibold">Top Pitchers</h2><ValueBarChart data={data.top_pitchers} yKey="projection" /></div>
        <div className="card"><h2 className="font-semibold">Top Value Bats</h2><ValueBarChart data={data.top_values} yKey="value_score" /></div>
        <div className="card"><h2 className="font-semibold">Top Stacks</h2><ValueBarChart data={data.top_stacks} xKey="team" yKey="stack_score" /></div>
        <div className="card"><h2 className="font-semibold">Refresh Timestamp</h2><p>{data.refreshed_at || 'No refresh yet'}</p></div>
      </div>
    </div>
  )
}
