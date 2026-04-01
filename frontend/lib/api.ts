const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchApi(path: string) {
  const r = await fetch(`${API_URL}${path}`, { cache: 'no-store' });
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}
