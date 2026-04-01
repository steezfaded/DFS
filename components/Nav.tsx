import Link from 'next/link';

const links = ['/', '/hitters', '/pitchers', '/stacks', '/games', '/lineup-builder'];

export function Nav() {
  return (
    <nav className="flex gap-3 p-4 border-b border-slate-800 sticky top-0 bg-slate-950 z-20">
      {links.map((l) => (
        <Link key={l} href={l} className="text-sm text-slate-300 hover:text-white">{l === '/' ? 'overview' : l.slice(1)}</Link>
      ))}
    </nav>
  );
}
