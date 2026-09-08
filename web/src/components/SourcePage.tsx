import { useState } from "react";

export function SourcePage({ snapshot, page }: { snapshot: string; page: number }) {
  const [open, setOpen] = useState(false);
  const src = `pages/${snapshot}/p${page}.png`;
  return (
    <>
      <button className="rounded border border-accent px-2 py-1 text-xs text-accent hover:bg-ground" onClick={() => setOpen(true)}>
        Source page · {snapshot} p.{page}
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-6" onClick={() => setOpen(false)}>
          <div className="max-h-full max-w-5xl overflow-auto rounded bg-surface p-2" onClick={(e) => e.stopPropagation()}>
            <div className="mb-2 flex items-center justify-between text-sm"><span>MoSPI Flash Report {snapshot}, page {page} (rendered from the PDF)</span>
              <button className="text-accent" onClick={() => setOpen(false)}>Close</button></div>
            <img src={src} alt={`Flash Report ${snapshot} page ${page}`} className="max-w-full"
              onError={(e) => { (e.currentTarget as HTMLImageElement).alt = "Page image not rendered — run python tools/render_pages.py"; }} />
          </div>
        </div>
      )}
    </>
  );
}
