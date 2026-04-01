'use client';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { fetchApi } from '../../../lib/api';

export default function PlayerPage() {
  const params = useParams<{id:string}>();
  const [p, setP] = useState<any | null>(null);
  useEffect(() => { if (params?.id) fetchApi(`/api/player/${params.id}`).then(setP).catch(()=>setP({name:'Unknown', positions:'N/A', is_pitcher:false})); }, [params?.id]);
  if (!p) return <div className="card">Loading player...</div>;
  return <div className="space-y-3"><h1 className="text-2xl font-bold">{p.name}</h1><div className="card"><p>Positions: {p.positions || 'N/A'}</p><p>Type: {p.is_pitcher ? 'Pitcher' : 'Hitter'}</p><p>Data quality note: public feeds may lag same-day lineup and status changes.</p></div></div>
}
