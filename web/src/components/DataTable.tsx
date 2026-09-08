import { flexRender, getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef, useState } from "react";

export function DataTable<T>({ columns, rows, onRowClick, height = "520px" }:
  { columns: ColumnDef<T, unknown>[]; rows: T[]; onRowClick?: (row: T) => void; height?: string }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({ data: rows, columns, state: { sorting }, onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(), getSortedRowModel: getSortedRowModel() });
  const parentRef = useRef<HTMLDivElement>(null);
  const trows = table.getRowModel().rows;
  const v = useVirtualizer({ count: trows.length, getScrollElement: () => parentRef.current, estimateSize: () => 36, overscan: 12 });
  const items = v.getVirtualItems();
  const before = items.length ? items[0].start : 0;
  const after = items.length ? v.getTotalSize() - items[items.length - 1].end : 0;
  return (
    <div ref={parentRef} className="overflow-auto rounded border border-line bg-surface" style={{ height }}>
      <table className="w-full border-collapse text-sm">
        <thead className="sticky top-0 z-10 bg-surface">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th key={h.id} onClick={h.column.getToggleSortingHandler()}
                  className="cursor-pointer select-none border-b border-line px-3 py-2 text-left text-xs uppercase tracking-wide text-muted">
                  {flexRender(h.column.columnDef.header, h.getContext())}
                  {{ asc: " ↑", desc: " ↓" }[h.column.getIsSorted() as string] ?? ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {before > 0 && <tr><td colSpan={columns.length} style={{ height: `${before}px` }} /></tr>}
          {items.map((vi) => {
            const row = trows[vi.index];
            return (
              <tr key={row.id} onClick={() => onRowClick?.(row.original)}
                className={`border-b border-line ${onRowClick ? "cursor-pointer hover:bg-ground" : ""}`} style={{ height: "36px" }}>
                {row.getVisibleCells().map((c) => <td key={c.id} className="px-3 py-1 align-middle">{flexRender(c.column.columnDef.cell, c.getContext())}</td>)}
              </tr>
            );
          })}
          {after > 0 && <tr><td colSpan={columns.length} style={{ height: `${after}px` }} /></tr>}
        </tbody>
      </table>
      {rows.length === 0 && <div className="p-6 text-sm text-muted">Nothing to show for this filter.</div>}
    </div>
  );
}
