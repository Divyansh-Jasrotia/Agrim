import { useState } from "react";

const MISSING = "Page image not rendered — run python tools/render_pages.py";

// inline renders the real rendered page instead of hiding it behind a chip. The height is
// bounded: a full A4 government page at half container width is unreadable anyway, and two of
// them unbounded push the rest of the screen off the bottom. Click opens the page full size.
export function SourcePage({ snapshot, page, inline = false, caption }:
  { snapshot: string; page: number; inline?: boolean; caption?: string }) {
  const [open, setOpen] = useState(false);
  const src = `pages/${snapshot}/p${page}.png`;
  const alt = `Flash Report ${snapshot} page ${page}`;
  const onError = (e: React.SyntheticEvent<HTMLImageElement>) => { (e.currentTarget as HTMLImageElement).alt = MISSING; };

  const modal = open && (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-6" onClick={() => setOpen(false)}>
      <div className="max-h-full max-w-5xl overflow-auto rounded bg-surface p-2" onClick={(e) => e.stopPropagation()}>
        <div className="mb-2 flex items-center justify-between text-sm">
          <span>MoSPI Flash Report {snapshot}, page {page} (rendered from the PDF)</span>
          <button className="text-accent" onClick={() => setOpen(false)}>Close</button>
        </div>
        <img src={src} alt={alt} className="max-w-full" onError={onError} />
      </div>
    </div>
  );

  if (inline) {
    return (
      <figure className="m-0 min-w-0">
        <button type="button" onClick={() => setOpen(true)} className="block w-full cursor-zoom-in"
          aria-label={`Open ${alt} full size`}>
          <img src={src} alt={alt} onError={onError}
            className="max-h-[360px] w-full rounded border border-line bg-surface object-contain object-top" />
        </button>
        <figcaption className="mt-1 text-xs text-muted">
          <span className="num">{snapshot}</span>, page <span className="num">{page}</span>, as printed
          {caption ? <> · {caption}</> : null} · click to open full size
        </figcaption>
        {modal}
      </figure>
    );
  }

  return (
    <>
      <button className="rounded border border-accent px-2 py-1 text-xs text-accent hover:bg-ground" onClick={() => setOpen(true)}>
        Source page · {snapshot} p.{page}
      </button>
      {modal}
    </>
  );
}
